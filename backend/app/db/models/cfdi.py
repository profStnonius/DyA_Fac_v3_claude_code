import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import UUID, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.db.models.base import TenantMixin, TimestampMixin, UUIDMixin


class CfdiDocument(UUIDMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "cfdi_documents"
    __table_args__ = (UniqueConstraint("uuid", name="uq_cfdi_uuid"),)

    xml_attachment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("email_attachments.id"))
    pdf_attachment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("email_attachments.id"))

    uuid: Mapped[str] = mapped_column(String(36), nullable=False)
    version: Mapped[str | None] = mapped_column(String(10))
    type: Mapped[str | None] = mapped_column(String(50))       # ingreso/egreso/traslado/nomina/pago
    direction: Mapped[str | None] = mapped_column(String(20))  # received/issued

    fecha_emision: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_timbrado: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    moneda: Mapped[str | None] = mapped_column(String(10))
    tipo_cambio: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    descuento: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    total_impuestos_trasladados: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    total_impuestos_retenidos: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    total: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))

    forma_pago: Mapped[str | None] = mapped_column(String(10))
    metodo_pago: Mapped[str | None] = mapped_column(String(10))
    uso_cfdi: Mapped[str | None] = mapped_column(String(10))
    lugar_expedicion: Mapped[str | None] = mapped_column(String(10))
    serie: Mapped[str | None] = mapped_column(String(25))
    folio: Mapped[str | None] = mapped_column(String(40))
    sello_sat: Mapped[str | None] = mapped_column(Text)
    no_certificado_sat: Mapped[str | None] = mapped_column(String(20))

    parse_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    parse_error: Mapped[str | None] = mapped_column(Text)
    raw_xml_path: Mapped[str | None] = mapped_column(Text)

    parties: Mapped[list["CfdiParty"]] = relationship(back_populates="cfdi_document")
    items: Mapped[list["CfdiItem"]] = relationship(back_populates="cfdi_document")
    taxes: Mapped[list["CfdiTax"]] = relationship(back_populates="cfdi_document")


class CfdiParty(UUIDMixin, TenantMixin, Base):
    __tablename__ = "cfdi_parties"

    cfdi_document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cfdi_documents.id"))
    party_type: Mapped[str] = mapped_column(String(20), nullable=False)  # emisor/receptor
    rfc: Mapped[str | None] = mapped_column(String(13))
    nombre: Mapped[str | None] = mapped_column(String(500))
    regimen_fiscal: Mapped[str | None] = mapped_column(String(10))
    domicilio_fiscal: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    cfdi_document: Mapped["CfdiDocument"] = relationship(back_populates="parties")


class CfdiItem(UUIDMixin, TenantMixin, Base):
    __tablename__ = "cfdi_items"

    cfdi_document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cfdi_documents.id"))
    item_index: Mapped[int] = mapped_column(Integer, nullable=False)
    clave_prod_serv: Mapped[str | None] = mapped_column(String(10))
    clave_unidad: Mapped[str | None] = mapped_column(String(10))
    no_identificacion: Mapped[str | None] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(Text)
    cantidad: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    valor_unitario: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    descuento: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    importe: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    objeto_imp: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    cfdi_document: Mapped["CfdiDocument"] = relationship(back_populates="items")
    taxes: Mapped[list["CfdiTax"]] = relationship(back_populates="cfdi_item")


class CfdiTax(UUIDMixin, TenantMixin, Base):
    __tablename__ = "cfdi_taxes"

    cfdi_document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cfdi_documents.id"))
    cfdi_item_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("cfdi_items.id"))
    tax_type: Mapped[str] = mapped_column(String(20), nullable=False)  # traslado/retencion
    impuesto: Mapped[str | None] = mapped_column(String(10))
    tipo_factor: Mapped[str | None] = mapped_column(String(20))
    tasa_cuota: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    importe: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    cfdi_document: Mapped["CfdiDocument"] = relationship(back_populates="taxes")
    cfdi_item: Mapped["CfdiItem"] = relationship(back_populates="taxes")
