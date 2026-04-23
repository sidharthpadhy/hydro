import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin


@dataclass
class JobConfig:
    workspace: str
    terrain_path: str
    streams_path: str
    parameters: dict


class HecRasRunner:
    def run_model(self, job_config: JobConfig) -> dict[str, str]:
        raise NotImplementedError


class WorkerUnavailableError(RuntimeError):
    pass


def ensure_real_worker_available(heartbeat_path: str, max_age_seconds: int) -> dict:
    heartbeat_file = Path(heartbeat_path)
    if not heartbeat_file.exists():
        raise WorkerUnavailableError(f"HEC-RAS worker heartbeat not found at {heartbeat_file}")

    try:
        payload = json.loads(heartbeat_file.read_text())
    except json.JSONDecodeError as exc:
        raise WorkerUnavailableError("HEC-RAS worker heartbeat is not valid JSON") from exc

    required = ["worker_id", "updated_at", "hec_ras_ready"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise WorkerUnavailableError(f"HEC-RAS worker heartbeat missing fields: {', '.join(missing)}")

    if payload["hec_ras_ready"] is not True:
        raise WorkerUnavailableError("HEC-RAS worker is present but not marked ready")

    try:
        updated_at = datetime.fromisoformat(str(payload["updated_at"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise WorkerUnavailableError("HEC-RAS worker heartbeat has an invalid updated_at timestamp") from exc

    now = datetime.now(timezone.utc)
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    if now - updated_at > timedelta(seconds=max_age_seconds):
        raise WorkerUnavailableError("HEC-RAS worker heartbeat is stale")

    return payload


class MockHecRasRunner(HecRasRunner):
    def run_model(self, job_config: JobConfig) -> dict[str, str]:
        workspace = Path(job_config.workspace)
        workspace.mkdir(parents=True, exist_ok=True)
        depth = workspace / "flood_depth_25yr.tif"
        wse = workspace / "water_surface_elevation_25yr.tif"
        for out in (depth, wse):
            arr = (np.random.rand(128, 128) * 3).astype("float32")
            with rasterio.open(
                out,
                "w",
                driver="GTiff",
                width=arr.shape[1],
                height=arr.shape[0],
                count=1,
                dtype="float32",
                crs=job_config.parameters.get("crs", "EPSG:3857"),
                transform=from_origin(0, 0, 30, 30),
            ) as dst:
                dst.write(arr, 1)

        summary = workspace / "run_summary.json"
        summary.write_text('{"scenario": "25-year", "runner": "mock"}')
        log = workspace / "run.log"
        log.write_text("Mock HEC-RAS run complete")
        return {
            "depth": str(depth),
            "wse": str(wse),
            "summary": str(summary),
            "log": str(log),
        }
