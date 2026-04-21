import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CfdiPartyOut(BaseModel):
    party_type: str
    rfc: str | None
    nombre: str | None
    regimen_fiscal: str | None

    model_config = {"from_attributes": True}


class CfdiItemOut(BaseModel):
    item_index: int
    clave_prod_serv: str | None
    no_identificacion: str | None
    descripcion: str | None
    cantidad: Decimal | None
    valor_unitario: Decimal | None
    descuento: Decimal | None
    importe: Decimal | None

    model_config = {"from_attributes": True}


class CfdiDocumentOut(BaseModel):
    id: uuid.UUID
    uuid: str
    version: str | None
    type: str | None
    direction: str | None
    fecha_emision: datetime | None
    moneda: str | None
    subtotal: Decimal | None
    total: Decimal | None
    parse_status: str

    model_config = {"from_attributes": True}


class CfdiDocumentDetail(CfdiDocumentOut):
    descuento: Decimal | None
    total_impuestos_trasladados: Decimal | None
    total_impuestos_retenidos: Decimal | None
    forma_pago: str | None
    metodo_pago: str | None
    uso_cfdi: str | None
    lugar_expedicion: str | None
    serie: str | None
    folio: str | None
    parties: list[CfdiPartyOut]
    items: list[CfdiItemOut]


class CfdiDocumentList(BaseModel):
    items: list[CfdiDocumentOut]
    total: int
    page: int
    page_size: int
