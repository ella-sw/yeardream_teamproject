from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        pass


@contextmanager
def fixture_site():
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(PROJECT_ROOT / "tests/fixtures_site"), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}/index.html"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def m1_expected() -> list[dict]:
    return json.loads((PROJECT_ROOT / "tests/expected/m1_findings.json").read_text(encoding="utf-8"))


@pytest.fixture
def site():
    with fixture_site() as url:
        yield url
