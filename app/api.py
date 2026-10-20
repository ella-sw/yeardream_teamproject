from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import resource_path
from app.jobs import cancel_job, get_job, shutdown_jobs, start_job
from app.models import ScanRequest, ScanStatus
from app.safety import UnsafeTarget, validate_http_url


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    shutdown_jobs()


app = FastAPI(title="공공 웹사이트 불법광고 탐지 도구", version="0.1.0", lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])
app.mount("/static", StaticFiles(directory=resource_path("app/static")), name="static")


@app.middleware("http")
async def same_origin_for_mutations(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin:
            expected = f"{request.url.scheme}://{request.headers.get('host', '')}"
            if origin.rstrip("/") != expected.rstrip("/"):
                return JSONResponse({"detail": "Cross-origin state changes are not allowed."}, status_code=403)
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'")
    return response


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(resource_path("app/static/index.html"))


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/scans", response_model=ScanStatus, status_code=202)
def create_scan(body: ScanRequest) -> ScanStatus:
    started_at = datetime.now().astimezone()
    try:
        validate_http_url(body.entry_url)
    except UnsafeTarget as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        runtime = start_job(body.entry_url, started_at)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ScanStatus(
        job_id=runtime.job_id,
        state=runtime.state,
        entry_url=runtime.entry_url,
        progress=runtime.progress,
        started_at=runtime.started_at,
    )


@app.get("/api/scans/{job_id}", response_model=ScanStatus)
def scan_status(job_id: str) -> ScanStatus:
    runtime = get_job(job_id)
    if runtime is None:
        raise HTTPException(status_code=404, detail="Scan job not found.")
    return ScanStatus(
        job_id=runtime.job_id,
        state=runtime.state,
        entry_url=runtime.entry_url,
        progress=runtime.progress,
        started_at=runtime.started_at,
        finished_at=runtime.finished_at,
        error=runtime.error,
        result_path=runtime.result_path,
    )


@app.post("/api/scans/{job_id}/cancel", status_code=202)
def stop_scan(job_id: str) -> dict:
    runtime = cancel_job(job_id)
    if runtime is None:
        raise HTTPException(status_code=404, detail="Scan job not found.")
    return {"job_id": job_id, "state": runtime.state, "cancel_requested": runtime.state.value in {"QUEUED", "RUNNING"}}


@app.get("/api/scans/{job_id}/result")
def scan_result(job_id: str) -> JSONResponse:
    runtime = get_job(job_id)
    if runtime is None:
        raise HTTPException(status_code=404, detail="Scan job not found.")
    if runtime.state != "COMPLETED" or not runtime.result:
        raise HTTPException(status_code=409, detail=f"A result is not available for state {runtime.state.value}.")
    return JSONResponse(runtime.result, headers={"Cache-Control": "no-store"})
