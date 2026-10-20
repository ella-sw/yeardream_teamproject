from __future__ import annotations

import json
import os
import socket
import threading
import time
from datetime import datetime
from pathlib import Path

import jsonschema
import uvicorn
from playwright.sync_api import sync_playwright
from app.api import app
from app.config import resource_path
from app.crawler.scan import scan_site
from tests.conftest import fixture_site, m1_expected


def test_c00_environment_and_chromium_startup() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        version = browser.version
        page = browser.new_page()
        page.set_content("<main>browser-ready</main>")
        assert page.locator("main").inner_text() == "browser-ready"
        browser.close()
    print(f"OS=macOS; Python={os.sys.version.split()[0]}; Chromium={version}; arch={os.uname().machine}")


def test_c01_real_page_offscreen_detection_and_unique_location(site: str, monkeypatch, tmp_path: Path) -> None:
    origin = site.rsplit("/", 1)[0]
    monkeypatch.setenv("SCANNER_ALLOWED_TEST_ORIGINS", origin)
    monkeypatch.setenv("SCANNER_OUTPUT_DIR", str(tmp_path))

    result, report = scan_site(site, datetime.now().astimezone())
    expected = m1_expected()
    assert report["pages_done"] == 1
    assert len(result.findings) == len(expected) == 1
    finding = result.findings[0]
    assert finding.evidence_text == expected[0]["evidence_text"]
    assert finding.technique.value == expected[0]["technique"]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(site, wait_until="domcontentloaded")
        locator = page.locator(finding.location)
        assert locator.count() == 1
        assert locator.evaluate("element => element.tagName.toLowerCase()") == expected[0]["target_tag"]
        assert locator.evaluate("element => element.textContent") == finding.evidence_text
        browser.close()


def test_c02_actual_ui_scan_creates_schema_valid_result(site: str, monkeypatch, tmp_path: Path) -> None:
    origin = site.rsplit("/", 1)[0]
    monkeypatch.setenv("SCANNER_ALLOWED_TEST_ORIGINS", origin)
    monkeypatch.setenv("SCANNER_OUTPUT_DIR", str(tmp_path / "output"))

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error", lifespan="on"))
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    base_url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.05)
        else:
            raise AssertionError("The local UI server did not start.")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(base_url, wait_until="domcontentloaded")
            assert page.get_by_role("heading", name="새 검사").is_visible()
            page.get_by_label("진입 URL").fill(site)
            page.get_by_role("button", name="검사 시작").click()
            page.get_by_role("heading", name="검사 완료").wait_for(timeout=20_000)
            rows = page.locator("#findings-body tr")
            assert rows.count() == 1
            assert rows.nth(0).inner_text().find("OFFSCREEN") >= 0
            assert rows.nth(0).inner_text().find("카지노 가입 보너스 안내") >= 0

            result_url = page.locator("#result-file").get_attribute("href")
            assert result_url
            result_response = page.request.get(f"{base_url}{result_url}")
            assert result_response.status == 200
            result_payload = result_response.json()
            browser.close()
    finally:
        server.should_exit = True
        server_thread.join(timeout=5)
        if server_thread.is_alive():
            raise AssertionError("The local UI server did not stop cleanly.")

    schema = json.loads(resource_path("schemas/result.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(result_payload)
    assert result_payload["findings"][0]["evidence_text"] == m1_expected()[0]["evidence_text"]

    output_dir = tmp_path / "output"
    result_bytes = (output_dir / "result.json").read_bytes()
    assert not result_bytes.startswith(b"\xef\xbb\xbf")
    assert json.loads(result_bytes.decode("utf-8")) == result_payload
