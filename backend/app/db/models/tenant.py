import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.db.models.base import TimestampMixin, UUIDMixin


class Tenant(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rfc: Mapped[str | None] = mapped_column(String(13))
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    settings: Mapped["TenantSettings"] = relationship(back_populates="tenant", uselist=False)
    user_roles: Mapped[list["UserTenantRole"]] = relationship(back_populates="tenant")


class TenantSettings(UUIDMixin, Base):
    __tablename__ = "tenant_settings"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    default_template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    gmail_sync_schedule: Mapped[str | None] = mapped_column(String(50))
    notification_email: Mapped[str | None] = mapped_column(String(255))
    timezone: Mapped[str] = mapped_column(String(50), default="America/Mexico_City")
    fiscal_year_start_month: Mapped[int] = mapped_column(Integer, default=1)
    settings_json: Mapped[dict | None] = mapped_column(JSONB)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="settings")


# Avoid circular import — import here after definitions
from app.db.models.user import UserTenantRole  # noqa: E402
