from __future__ import annotations

import multiprocessing
import os
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

import uvicorn


APP_URL = "http://127.0.0.1:8765"


def open_ui_when_ready() -> None:
    for _ in range(50):
        try:
            with urllib.request.urlopen(f"{APP_URL}/api/health", timeout=0.5):
                webbrowser.open(APP_URL)
                return
        except OSError:
            time.sleep(0.2)


def main() -> None:
    multiprocessing.freeze_support()
    os.environ.setdefault("SCANNER_UI_ORIGIN", APP_URL)
    if getattr(sys, "frozen", False):
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(Path(sys.executable).resolve().parent / "ms-playwright"))
    threading.Thread(target=open_ui_when_ready, daemon=True).start()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8765, log_level="info")


if __name__ == "__main__":
    main()
