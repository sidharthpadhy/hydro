import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JobStatus(str, enum.Enum):
    queued = "queued"
    preprocessing = "preprocessing"
    running = "running"
    failed = "failed"
    completed = "completed"


class AssetType(str, enum.Enum):
    dem = "dem"
    streams = "streams"
    result = "result"


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UploadedAsset(Base):
    __tablename__ = "uploaded_assets"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType))
    file_name: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ModelJob(Base):
    __tablename__ = "model_jobs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    dem_asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_assets.id"))
    streams_asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_assets.id"))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.queued)
    workspace_path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    parameters = relationship("ModelParameters", back_populates="job", uselist=False)


class ModelParameters(Base):
    __tablename__ = "model_parameters"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_jobs.id"), unique=True)
    peak_flow_cms: Mapped[float] = mapped_column(Float)
    hydrograph_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    mannings_n: Mapped[float] = mapped_column(Float)
    upstream_bc: Mapped[str] = mapped_column(Text)
    downstream_bc: Mapped[str] = mapped_column(Text)
    simulation_start: Mapped[str] = mapped_column(String(64))
    simulation_end: Mapped[str] = mapped_column(String(64))
    mesh_cell_size: Mapped[float] = mapped_column(Float)
    crs: Mapped[str] = mapped_column(String(64))
    units: Mapped[str] = mapped_column(String(16))

    job = relationship("ModelJob", back_populates="parameters")


class ResultAsset(Base):
    __tablename__ = "result_assets"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_jobs.id"))
    file_name: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(Text)
    asset_type: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobEvent(Base):
    __tablename__ = "job_events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_jobs.id"))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
