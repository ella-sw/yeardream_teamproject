from __future__ import annotations

import multiprocessing
import queue
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.config import output_root
from app.models import ProgressEvent, ScanState
from app.worker import scan_worker


@dataclass
class JobRuntime:
    job_id: str
    entry_url: str
    started_at: datetime
    process: multiprocessing.Process
    events: multiprocessing.queues.Queue
    stop_event: multiprocessing.synchronize.Event
    run_dir: Path
    state: ScanState = ScanState.QUEUED
    progress: ProgressEvent = field(default_factory=ProgressEvent)
    finished_at: datetime | None = None
    error: str | None = None
    result_path: str | None = None
    result: dict | None = None
    report: dict | None = None


_jobs: dict[str, JobRuntime] = {}
_lock = threading.RLock()


def _drain(runtime: JobRuntime) -> None:
    def apply(event: dict) -> None:
        event_type = event.get("type")
        if event_type == "progress":
            runtime.progress = ProgressEvent(**event["progress"])
        elif event_type == "completed":
            runtime.result = event["result"]
            runtime.report = event["report"]
            runtime.result_path = event["result_path"]
            runtime.progress = ProgressEvent(
                pages_done=event["report"].get("pages_done", 0),
                pending_pages=event["report"].get("pending_pages", 0),
                finding_count=event["report"].get("finding_count", 0),
                warnings=event["report"].get("warnings", []),
            )
            runtime.state = ScanState.COMPLETED
            runtime.finished_at = datetime.now().astimezone()
        elif event_type == "cancelled":
            runtime.report = event["report"]
            runtime.error = event["report"].get("error")
            runtime.state = ScanState.CANCELLED
            runtime.finished_at = datetime.now().astimezone()
        elif event_type == "failed":
            runtime.report = event["report"]
            runtime.error = event["error"]
            runtime.state = ScanState.FAILED
            runtime.finished_at = datetime.now().astimezone()

    while True:
        try:
            event = runtime.events.get_nowait()
        except queue.Empty:
            break
        apply(event)

    if not runtime.process.is_alive():
        runtime.process.join(timeout=0)
        # multiprocessing.Queue may flush a final child message just after exit.
        for _ in range(10):
            try:
                event = runtime.events.get(timeout=0.02)
            except queue.Empty:
                break
            apply(event)
        if runtime.state in {ScanState.QUEUED, ScanState.RUNNING}:
            runtime.state = ScanState.FAILED
            runtime.error = f"Scanner worker exited with code {runtime.process.exitcode} without a final result."
            runtime.finished_at = datetime.now().astimezone()


def start_job(entry_url: str, started_at: datetime | None = None) -> JobRuntime:
    with _lock:
        for existing in _jobs.values():
            _drain(existing)
            if existing.process.is_alive():
                raise RuntimeError("A scan is already running.")

        context = multiprocessing.get_context("spawn")
        job_id = uuid4().hex
        start_time = started_at or datetime.now().astimezone()
        root = output_root()
        run_dir = root / ".runs" / job_id
        events = context.Queue()
        stop_event = context.Event()
        process = context.Process(
            target=scan_worker,
            args=(entry_url, start_time, str(root), str(run_dir), job_id, events, stop_event),
            name=f"scan-{job_id[:8]}",
            daemon=True,
        )
        runtime = JobRuntime(job_id, entry_url, start_time, process, events, stop_event, run_dir)
        _jobs[job_id] = runtime
        process.start()
        runtime.state = ScanState.RUNNING
        return runtime


def get_job(job_id: str) -> JobRuntime | None:
    with _lock:
        runtime = _jobs.get(job_id)
        if runtime:
            _drain(runtime)
        return runtime


def cancel_job(job_id: str) -> JobRuntime | None:
    with _lock:
        runtime = _jobs.get(job_id)
        if not runtime:
            return None
        _drain(runtime)
        if runtime.state in {ScanState.QUEUED, ScanState.RUNNING}:
            runtime.stop_event.set()
        return runtime


def shutdown_jobs() -> None:
    with _lock:
        runtimes = list(_jobs.values())
    for runtime in runtimes:
        if runtime.process.is_alive():
            runtime.stop_event.set()
            runtime.process.join(timeout=2)
        if runtime.process.is_alive():
            # The process belongs to this app; no unrelated browser is touched.
            runtime.process.terminate()
            runtime.process.join(timeout=1)
    with _lock:
        _jobs.clear()
