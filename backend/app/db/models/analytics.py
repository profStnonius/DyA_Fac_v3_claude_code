import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.db.models.base import TenantMixin, TimestampMixin, UUIDMixin


class AnalyticsSnapshot(UUIDMixin, TenantMixin, Base):
    __tablename__ = "analytics_snapshots"

    snapshot_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # monthly_sales / top_products / top_clients / profit_by_product / etc.
    period_year: Mapped[int | None] = mapped_column(Integer)
    period_month: Mapped[int | None] = mapped_column(Integer)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ProductsCatalog(UUIDMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "products_catalog"

    clave_sat: Mapped[str | None] = mapped_column(String(10))
    descripcion_normalizada: Mapped[str] = mapped_column(Text, nullable=False)
    alias: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    cost_reference: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))


class ClientsCatalog(UUIDMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "clients_catalog"

    rfc: Mapped[str | None] = mapped_column(String(13))
    nombre: Mapped[str] = mapped_column(String(500), nullable=False)
    segmento: Mapped[str | None] = mapped_column(String(100))


class SuppliersCatalog(UUIDMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "suppliers_catalog"

    rfc: Mapped[str | None] = mapped_column(String(13))
    nombre: Mapped[str] = mapped_column(String(500), nullable=False)
