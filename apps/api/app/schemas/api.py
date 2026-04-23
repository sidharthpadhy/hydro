from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class UploadResponse(BaseModel):
    asset_id: UUID
    filename: str
    metadata: dict[str, Any]


class ScenarioInput(BaseModel):
    peak_flow_cms: float = Field(gt=0)
    hydrograph_json: dict[str, Any] | None = None
    mannings_n: float = Field(gt=0)
    upstream_bc: str
    downstream_bc: str
    simulation_start: datetime
    simulation_end: datetime
    mesh_cell_size: float = Field(gt=0)
    crs: str
    units: str

    @model_validator(mode="after")
    def validate_window(self) -> "ScenarioInput":
        if self.simulation_end <= self.simulation_start:
            raise ValueError("simulation_end must be after simulation_start")
        return self


class CreateJobRequest(BaseModel):
    dem_asset_id: UUID
    streams_asset_id: UUID
    parameters: ScenarioInput


class JobResponse(BaseModel):
    job_id: UUID
    status: str
    created_at: datetime


class JobDetails(JobResponse):
    events: list[dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
