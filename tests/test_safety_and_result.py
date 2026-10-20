from __future__ import annotations

import json

import pytest

from app.models import ResultDocument, ResultMeta
from app.result.writer import serialize_result
from app.safety import UnsafeTarget, authorize_network_url, validate_http_url


@pytest.mark.parametrize("url", [
    "file:///etc/passwd",
    "javascript:alert(1)",
    "http://user:password@example.com/",
    "http://127.0.0.1/",
    "http://localhost/",
    "http://127.0.0.1:0/",
])
def test_private_or_non_http_targets_are_rejected_by_default(url: str, monkeypatch) -> None:
    monkeypatch.delenv("SCANNER_ALLOWED_TEST_ORIGINS", raising=False)
    with pytest.raises(UnsafeTarget):
        validate_http_url(url)


def test_exact_test_origin_can_allow_loopback_but_not_other_ports(monkeypatch) -> None:
    monkeypatch.setenv("SCANNER_ALLOWED_TEST_ORIGINS", "http://127.0.0.1:9021")
    assert validate_http_url("http://127.0.0.1:9021/index.html") == "http://127.0.0.1:9021"
    with pytest.raises(UnsafeTarget):
        validate_http_url("http://127.0.0.1:9022/index.html")


def test_scanner_control_origin_stays_blocked_even_when_test_origin_is_allowed(monkeypatch) -> None:
    monkeypatch.setenv("SCANNER_UI_ORIGIN", "http://127.0.0.1:8765")
    monkeypatch.setenv("SCANNER_ALLOWED_TEST_ORIGINS", "http://127.0.0.1:8765")
    with pytest.raises(UnsafeTarget, match="control UI"):
        authorize_network_url("http://127.0.0.1:8765/api/health")


def test_zero_findings_result_is_valid_utf8_json_without_bom() -> None:
    result = ResultDocument(meta=ResultMeta(
        topic="TOPIC",
        entry_url="https://example.invalid/",
        started_at="2026-10-20T10:00:00+09:00",
        finished_at="2026-10-20T10:00:01+09:00",
        elapsed_sec=1,
    ), findings=[])
    payload = serialize_result(result)
    assert not payload.startswith(b"\xef\xbb\xbf")
    assert json.loads(payload.decode("utf-8"))["findings"] == []
