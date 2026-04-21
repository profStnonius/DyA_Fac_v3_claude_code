import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.db.models.base import TenantMixin, UUIDMixin


class ProcessingJob(UUIDMixin, TenantMixin, Base):
    __tablename__ = "processing_jobs"

    triggered_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # email_sync / cfdi_parse / batch_zip / analytics_refresh / report_export
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    # pending / running / completed / failed / cancelled
    celery_task_id: Mapped[str | None] = mapped_column(String(255))
    input_payload: Mapped[dict | None] = mapped_column(JSONB)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    total_items: Mapped[int | None] = mapped_column(Integer)
    processed_items: Mapped[int] = mapped_column(Integer, default=0)
    failed_items: Mapped[int] = mapped_column(Integer, default=0)
    output_artifact_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("export_files.id"))
    error_detail: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class BatchDataset(UUIDMixin, TenantMixin, Base):
    __tablename__ = "batch_datasets"

    processing_job_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("processing_jobs.id"))
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("extraction_templates.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer)
    column_config: Mapped[dict | None] = mapped_column(JSONB)
    storage_path: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


from app.db.models.export import ExportFile  # noqa: E402
