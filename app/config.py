from __future__ import annotations

import os
import sys
from pathlib import Path

APP_VERSION = "0.1.0"
PAGE_TIMEOUT_MS = 15_000
DOM_SETTLE_MS = 500
DOM_SETTLE_LIMIT_MS = 2_000


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resource_path(relative_path: str) -> Path:
    """Resolve bundled and source-tree resources without relying on cwd."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    root = Path(bundle_root) if bundle_root else project_root()
    return root / relative_path


def output_root() -> Path:
    configured = os.environ.get("SCANNER_OUTPUT_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return project_root()


def allowed_test_origins() -> set[str]:
    """Exact local origins explicitly enabled for a controlled test run."""
    raw = os.environ.get("SCANNER_ALLOWED_TEST_ORIGINS", "")
    return {item.strip().rstrip("/") for item in raw.split(",") if item.strip()}
