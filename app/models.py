from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Technique(str, Enum):
    HOMOGLYPH = "HOMOGLYPH"
    JAMO = "JAMO"
    TRANSPARENT = "TRANSPARENT"
    OFFSCREEN = "OFFSCREEN"


class ScanState(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ResultMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str = "TOPIC"
    entry_url: str
    started_at: datetime
    finished_at: datetime
    elapsed_sec: float = Field(ge=0)
    tool_version: str = "0.1.0"


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    url: str
    is_violation: bool = True
    location: str
    evidence_text: str
    technique: Technique


class ResultDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: ResultMeta
    findings: list[Finding]


class ScanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_url: str = Field(min_length=1, max_length=2048)


class ProgressEvent(BaseModel):
    pages_done: int = 0
    pending_pages: int = 1
    finding_count: int = 0
    warnings: list[str] = Field(default_factory=list)


class ScanStatus(BaseModel):
    job_id: str
    state: ScanState
    entry_url: str
    progress: ProgressEvent
    started_at: datetime
    finished_at: datetime | None = None
    error: str | None = None
    result_path: str | None = None
