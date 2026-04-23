from dataclasses import dataclass
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
