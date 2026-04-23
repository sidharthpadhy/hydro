from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.gis.preprocess import inspect_dem, inspect_kml
from app.models.entities import AssetType, JobEvent, ModelJob, ModelParameters, ResultAsset, UploadedAsset
from app.orchestration.jobs import run_job_pipeline
from app.schemas.api import CreateJobRequest, HealthResponse, JobDetails, JobResponse, UploadResponse
from app.services.validation import validate_dem_file, validate_streams_file
from app.storage.local import LocalStorageService

router = APIRouter(prefix="/api")
storage = LocalStorageService(settings.storage_root)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/uploads/dem", response_model=UploadResponse)
async def upload_dem(file: UploadFile = File(...), db: Session = Depends(get_db)) -> UploadResponse:
    body = await file.read()
    try:
        validate_dem_file(file.filename, len(body), settings.max_upload_mb)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    path = storage.save_bytes(body, file.filename)
    metadata = inspect_dem(path)
    asset = UploadedAsset(asset_type=AssetType.dem, file_name=file.filename, storage_path=path, metadata_json=metadata)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return UploadResponse(asset_id=asset.id, filename=file.filename, metadata=metadata)


@router.post("/uploads/streams", response_model=UploadResponse)
async def upload_streams(file: UploadFile = File(...), db: Session = Depends(get_db)) -> UploadResponse:
    body = await file.read()
    try:
        validate_streams_file(file.filename, len(body), settings.max_upload_mb)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    path = storage.save_bytes(body, file.filename)
    metadata = inspect_kml(path)
    asset = UploadedAsset(asset_type=AssetType.streams, file_name=file.filename, storage_path=path, metadata_json=metadata)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return UploadResponse(asset_id=asset.id, filename=file.filename, metadata=metadata)


@router.post("/jobs", response_model=JobResponse)
def create_job(payload: CreateJobRequest, db: Session = Depends(get_db)) -> JobResponse:
    dem = db.get(UploadedAsset, payload.dem_asset_id)
    streams = db.get(UploadedAsset, payload.streams_asset_id)
    if not dem or not streams:
        raise HTTPException(status_code=404, detail="Assets not found")

    workspace = str(Path(settings.workspace_root) / "pending")
    job = ModelJob(dem_asset_id=dem.id, streams_asset_id=streams.id, workspace_path=workspace)
    db.add(job)
    db.commit()
    db.refresh(job)

    params = ModelParameters(
        job_id=job.id,
        peak_flow_cms=payload.parameters.peak_flow_cms,
        hydrograph_json=payload.parameters.hydrograph_json,
        mannings_n=payload.parameters.mannings_n,
        upstream_bc=payload.parameters.upstream_bc,
        downstream_bc=payload.parameters.downstream_bc,
        simulation_start=payload.parameters.simulation_start.isoformat(),
        simulation_end=payload.parameters.simulation_end.isoformat(),
        mesh_cell_size=payload.parameters.mesh_cell_size,
        crs=payload.parameters.crs,
        units=payload.parameters.units,
    )
    db.add(params)
    db.commit()

    run_job_pipeline(db, job, dem.storage_path, streams.storage_path, payload.parameters.model_dump(mode="json"))
    return JobResponse(job_id=job.id, status=job.status.value, created_at=job.created_at)


@router.get("/jobs/{job_id}", response_model=JobDetails)
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> JobDetails:
    job = db.get(ModelJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    events = db.scalars(select(JobEvent).where(JobEvent.job_id == job.id).order_by(JobEvent.created_at.asc())).all()
    return JobDetails(
        job_id=job.id,
        status=job.status.value,
        created_at=job.created_at,
        events=[{"status": e.status.value, "message": e.message, "created_at": e.created_at.isoformat()} for e in events],
    )


@router.get("/jobs/{job_id}/results")
def get_results(job_id: UUID, db: Session = Depends(get_db)):
    rows = db.scalars(select(ResultAsset).where(ResultAsset.job_id == job_id)).all()
    return [{"asset_type": r.asset_type, "file_name": r.file_name, "download_url": f"/api/jobs/{job_id}/results/{r.id}"} for r in rows]


@router.get("/jobs/{job_id}/results/{result_id}")
def download_result(job_id: UUID, result_id: UUID, db: Session = Depends(get_db)):
    result = db.get(ResultAsset, result_id)
    if not result or result.job_id != job_id:
        raise HTTPException(status_code=404, detail="Result not found")
    return FileResponse(result.storage_path, filename=result.file_name)


@router.get("/jobs/{job_id}/logs")
def get_logs(job_id: UUID, db: Session = Depends(get_db)):
    rows = db.scalars(select(ResultAsset).where(ResultAsset.job_id == job_id, ResultAsset.asset_type == "log")).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Log not available")
    return FileResponse(rows[0].storage_path, filename=rows[0].file_name)


@router.get("/jobs/{job_id}/events")
def job_events(job_id: UUID, db: Session = Depends(get_db)):
    def stream():
        events = db.scalars(select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.created_at.asc())).all()
        for event in events:
            yield f"data: {event.status.value}|{event.message}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
