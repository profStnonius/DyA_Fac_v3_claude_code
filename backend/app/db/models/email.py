import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.db.models.base import TenantMixin, TimestampMixin, UUIDMixin


class EmailAccount(UUIDMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "email_accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    email_address: Mapped[str] = mapped_column(String(255), nullable=False)
    google_access_token: Mapped[str | None] = mapped_column(Text)   # Encrypted at rest
    google_refresh_token: Mapped[str | None] = mapped_column(Text)  # Encrypted at rest
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scopes: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    sync_jobs: Mapped[list["SyncJob"]] = relationship(back_populates="email_account")
    messages: Mapped[list["EmailMessage"]] = relationship(back_populates="email_account")


class SyncJob(UUIDMixin, TenantMixin, Base):
    __tablename__ = "sync_jobs"

    email_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("email_accounts.id"))
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    filter_config: Mapped[dict | None] = mapped_column(JSONB)
    total_messages: Mapped[int] = mapped_column(Integer, default=0)
    processed_messages: Mapped[int] = mapped_column(Integer, default=0)
    failed_messages: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_detail: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    email_account: Mapped["EmailAccount"] = relationship(back_populates="sync_jobs")
    messages: Mapped[list["EmailMessage"]] = relationship(back_populates="sync_job")


class EmailMessage(UUIDMixin, TenantMixin, Base):
    __tablename__ = "email_messages"

    email_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("email_accounts.id"))
    sync_job_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sync_jobs.id"))
    gmail_message_id: Mapped[str] = mapped_column(String(255), nullable=False)
    thread_id: Mapped[str | None] = mapped_column(String(255))
    from_address: Mapped[str | None] = mapped_column(String(255))
    subject: Mapped[str | None] = mapped_column(Text)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    email_account: Mapped["EmailAccount"] = relationship(back_populates="messages")
    sync_job: Mapped["SyncJob"] = relationship(back_populates="messages")
    attachments: Mapped[list["EmailAttachment"]] = relationship(back_populates="message")


class EmailAttachment(UUIDMixin, TenantMixin, Base):
    __tablename__ = "email_attachments"

    email_message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("email_messages.id"))
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(100))
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)
    storage_path: Mapped[str | None] = mapped_column(Text)
    storage_bucket: Mapped[str | None] = mapped_column(String(255))
    file_hash: Mapped[str | None] = mapped_column(String(64))  # SHA-256
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    message: Mapped["EmailMessage"] = relationship(back_populates="attachments")
