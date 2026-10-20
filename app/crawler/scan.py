from __future__ import annotations

from datetime import datetime
from typing import Callable

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from app.config import DOM_SETTLE_LIMIT_MS, DOM_SETTLE_MS, PAGE_TIMEOUT_MS
from app.detection.signals import has_advertising_context
from app.models import Finding, ResultDocument, ResultMeta, Technique
from app.safety import UnsafeTarget, authorize_network_url, validate_http_url


_EXTRACT_VISIBLE_AND_HIDDEN_TEXT = r"""() => {
  const ignored = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'SVG', 'PATH']);
  const elements = Array.from(document.body ? document.body.querySelectorAll('*') : []);

  function selectorFor(element) {
    const parts = [];
    let current = element;
    while (current && current !== document.body) {
      const tag = current.tagName.toLowerCase();
      const classes = Array.from(current.classList || []).map((name) => `.${CSS.escape(name)}`).join('');
      let part = `${tag}${classes}`;
      const parent = current.parentElement;
      if (!parent) break;
      const sameTag = Array.from(parent.children).filter((sibling) => sibling.tagName === current.tagName);
      const samePart = sameTag.filter((sibling) => {
        const siblingClasses = Array.from(sibling.classList || []).map((name) => `.${CSS.escape(name)}`).join('');
        return `${sibling.tagName.toLowerCase()}${siblingClasses}` === part;
      });
      if (samePart.length > 1) {
        part += `:nth-of-type(${sameTag.indexOf(current) + 1})`;
      }
      parts.unshift(part);
      current = parent;
    }
    const selector = `body > ${parts.join(' > ')}`;
    const matches = document.querySelectorAll(selector);
    return {
      selector,
      unique: matches.length === 1 && matches[0] === element,
      count: matches.length,
    };
  }

  return elements.filter((element) => !ignored.has(element.tagName)).map((element) => {
    const rawText = Array.from(element.childNodes)
      .filter((node) => node.nodeType === Node.TEXT_NODE)
      .map((node) => node.nodeValue || '')
      .join('');
    if (!rawText.trim()) return null;

    let hiddenReason = null;
    let owner = element;
    while (owner && owner !== document.documentElement) {
      if (getComputedStyle(owner).display === 'none') {
        hiddenReason = 'display:none';
        break;
      }
      owner = owner.parentElement;
    }
    if (!hiddenReason) return { rawText, hiddenReason: null, ...selectorFor(element) };
    return { rawText, hiddenReason, ...selectorFor(element) };
  }).filter(Boolean);
}"""


def scan_site(
    entry_url: str,
    started_at: datetime,
    progress: Callable[[dict], None] | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> tuple[ResultDocument, dict]:
    validate_http_url(entry_url)
    warnings: list[str] = []
    findings: list[Finding] = []
    pages_done = 0
    browser_version = "unknown"
    actual_url = entry_url

    def emit() -> None:
        if progress:
            progress({"pages_done": pages_done, "pending_pages": 0, "finding_count": len(findings), "warnings": list(warnings)})

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        browser_version = browser.version
        context = browser.new_context()
        page = context.new_page()

        def guard_request(route) -> None:
            request_url = route.request.url
            if request_url.startswith(("data:", "blob:", "about:")):
                route.continue_()
                return
            try:
                authorize_network_url(request_url)
            except UnsafeTarget as exc:
                warnings.append(f"Blocked network request: {request_url} ({exc})")
                route.abort()
                return
            route.continue_()

        page.route("**/*", guard_request)
        if cancelled and cancelled():
            context.close()
            browser.close()
            raise InterruptedError("Scan cancelled before navigation.")
        try:
            page.goto(entry_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            try:
                page.wait_for_load_state("networkidle", timeout=DOM_SETTLE_LIMIT_MS)
            except PlaywrightTimeoutError:
                page.wait_for_timeout(DOM_SETTLE_MS)
                warnings.append("The page did not reach network idle within the 2-second stabilization limit.")
            actual_url = page.url
            snapshots = page.evaluate(_EXTRACT_VISIBLE_AND_HIDDEN_TEXT)
        except PlaywrightTimeoutError as exc:
            context.close()
            browser.close()
            raise RuntimeError(f"The entry page did not load within {PAGE_TIMEOUT_MS} ms: {entry_url}") from exc
        except Exception:
            context.close()
            browser.close()
            raise

        for snapshot in snapshots:
            if cancelled and cancelled():
                context.close()
                browser.close()
                raise InterruptedError("Scan cancelled during page analysis.")
            if not snapshot["hiddenReason"] or not has_advertising_context(snapshot["rawText"]):
                continue
            if not snapshot["unique"]:
                warnings.append(f"Could not validate a unique CSS selector for text: {snapshot['rawText'][:120]}")
                continue
            if snapshot["hiddenReason"] == "display:none":
                findings.append(Finding(
                    id=f"f_{len(findings) + 1:06d}",
                    url=actual_url,
                    is_violation=True,
                    location=snapshot["selector"],
                    evidence_text=snapshot["rawText"],
                    technique=Technique.OFFSCREEN,
                ))

        pages_done = 1
        emit()
        context.close()
        browser.close()

    finished_at = datetime.now().astimezone()
    result = ResultDocument(meta=ResultMeta(
        topic="TOPIC",
        entry_url=entry_url,
        started_at=started_at,
        finished_at=finished_at,
        elapsed_sec=round(max(0.0, (finished_at - started_at).total_seconds()), 3),
        tool_version="0.1.0",
    ), findings=findings)
    report = {
        "state": "COMPLETED",
        "pages_done": pages_done,
        "pending_pages": 0,
        "finding_count": len(findings),
        "warnings": warnings,
        "browser_version": browser_version,
        "scope": "M1: one entry page, display:none OFFSCREEN rule only",
    }
    return result, report
