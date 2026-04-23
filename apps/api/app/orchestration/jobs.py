import json
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.adapters.hecras import JobConfig, MockHecRasRunner
from app.core.config import settings
from app.gis.preprocess import convert_kml_to_geojson, ensure_overlap, inspect_dem, inspect_kml
from app.models.entities import JobEvent, JobStatus, ModelJob, ResultAsset


def _event(db: Session, job_id: UUID, status: JobStatus, message: str) -> None:
    db.add(JobEvent(job_id=job_id, status=status, message=message))
    db.commit()


def run_job_pipeline(db: Session, job: ModelJob, dem_path: str, streams_path: str, params: dict) -> None:
    job.status = JobStatus.preprocessing
    db.commit()
    _event(db, job.id, JobStatus.preprocessing, "Preprocessing started")

    dem_meta = inspect_dem(dem_path)
    stream_meta = inspect_kml(streams_path)
    if not ensure_overlap(dem_meta["bounds"], stream_meta["bounds"]):
        job.status = JobStatus.failed
        db.commit()
        _event(db, job.id, JobStatus.failed, "DEM and streams do not overlap")
        return

    workspace = Path(settings.workspace_root) / str(job.id)
    workspace.mkdir(parents=True, exist_ok=True)
    streams_geojson = convert_kml_to_geojson(streams_path, str(workspace))

    job.status = JobStatus.running
    db.commit()
    _event(db, job.id, JobStatus.running, "Model execution started")

    runner = MockHecRasRunner()
    outputs = runner.run_model(
        JobConfig(
            workspace=str(workspace),
            terrain_path=dem_path,
            streams_path=streams_geojson,
            parameters=params,
        )
    )

    for key, path in outputs.items():
        db.add(ResultAsset(job_id=job.id, file_name=Path(path).name, storage_path=path, asset_type=key))

    extent = {"dem": dem_meta, "streams": stream_meta}
    (workspace / "preprocess_summary.json").write_text(json.dumps(extent, indent=2))

    job.status = JobStatus.completed
    db.commit()
    _event(db, job.id, JobStatus.completed, "Job completed")
