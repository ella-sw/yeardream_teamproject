from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from app.config import resource_path
from app.models import ResultDocument


def _write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def serialize_result(result: ResultDocument) -> bytes:
    payload = result.model_dump(mode="json")
    schema_path = resource_path("schemas/result.schema.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(payload)
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def archive_existing_result(output_dir: Path, job_id: str) -> None:
    history = output_dir / ".history" / job_id
    for name in ("result.json", "run_report.json"):
        current = output_dir / name
        if current.exists():
            history.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current), history / name)


def write_scan_artifacts(result: ResultDocument, report: dict, output_dir: Path, run_dir: Path, job_id: str) -> Path:
    result_bytes = serialize_result(result)
    report_bytes = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    run_result = run_dir / "result.json"
    _write_atomic(run_result, result_bytes)
    _write_atomic(run_dir / "run_report.json", report_bytes)
    _write_atomic(output_dir / "result.json", result_bytes)
    _write_atomic(output_dir / "run_report.json", report_bytes)
    return run_result


def write_failure_report(report: dict, output_dir: Path, run_dir: Path) -> None:
    content = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write_atomic(run_dir / "run_report.json", content)
    _write_atomic(output_dir / "run_report.json", content)
