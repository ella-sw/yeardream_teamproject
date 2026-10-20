from __future__ import annotations

import traceback
from datetime import datetime
from pathlib import Path

from app.crawler.scan import scan_site
from app.result.writer import archive_existing_result, write_failure_report, write_scan_artifacts


def scan_worker(entry_url: str, started_at: datetime, output_dir: str, run_dir: str, job_id: str, events, stop_event) -> None:
    output_path = Path(output_dir)
    job_path = Path(run_dir)
    job_path.mkdir(parents=True, exist_ok=True)
    try:
        archive_existing_result(output_path, job_id)

        def send_progress(progress: dict) -> None:
            events.put({"type": "progress", "progress": progress})

        result, report = scan_site(entry_url, started_at, send_progress, stop_event.is_set)
        write_scan_artifacts(result, report, output_path, job_path, job_id)
        result_path = str(output_path / "result.json")
        events.put({
            "type": "completed",
            "result": result.model_dump(mode="json"),
            "report": report,
            "result_path": str(result_path),
        })
    except InterruptedError as exc:
        report = {"state": "CANCELLED", "error": str(exc), "pages_done": 0, "pending_pages": 1, "warnings": []}
        write_failure_report(report, output_path, job_path)
        events.put({"type": "cancelled", "report": report})
    except Exception as exc:
        report = {"state": "FAILED", "error": str(exc), "traceback": traceback.format_exc(), "pages_done": 0, "pending_pages": 1, "warnings": []}
        try:
            write_failure_report(report, output_path, job_path)
        finally:
            events.put({"type": "failed", "error": str(exc), "report": report})
