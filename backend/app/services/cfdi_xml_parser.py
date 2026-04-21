"""
CFDI XML Parser — parses CFDI 3.3 and 4.0 XML documents to the canonical data model.

XML is the source of truth. In case of conflict with PDF, XML wins unless
explicit business rules state otherwise.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from lxml import etree

# SAT CFDI namespace map
CFDI_NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "cfdi33": "http://www.sat.gob.mx/cfd/3",
    "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital",
}

CFDI_4_NS = "http://www.sat.gob.mx/cfd/4"
CFDI_3_NS = "http://www.sat.gob.mx/cfd/3"


def parse_cfdi_xml_bytes(xml_bytes: bytes, tenant_id: uuid.UUID) -> dict[str, Any]:
    """
    Parse raw CFDI XML bytes into a canonical dict ready for DB insertion.
    Returns a dict with keys: document, parties, items, taxes.
    Raises ValueError for invalid/non-CFDI XML.
    """
    root = etree.fromstring(xml_bytes)
    ns = _detect_namespace(root)
    version = root.get("Version", root.get("version", ""))

    comprobante = {
        "uuid": _get_uuid(root, ns),
        "version": version,
        "type": root.get("TipoDeComprobante"),
        "fecha_emision": _parse_datetime(root.get("Fecha")),
        "moneda": root.get("Moneda"),
        "tipo_cambio": _decimal_or_none(root.get("TipoCambio")),
        "subtotal": _decimal_or_none(root.get("SubTotal")),
        "descuento": _decimal_or_none(root.get("Descuento")),
        "total": _decimal_or_none(root.get("Total")),
        "forma_pago": root.get("FormaPago"),
        "metodo_pago": root.get("MetodoPago"),
        "uso_cfdi": _get_uso_cfdi(root, ns, version),
        "lugar_expedicion": root.get("LugarExpedicion"),
        "serie": root.get("Serie"),
        "folio": root.get("Folio"),
        "no_certificado_sat": _get_no_certificado_sat(root, ns),
        "sello_sat": _get_sello_sat(root, ns),
    }

    parties = _parse_parties(root, ns, tenant_id)
    items, taxes = _parse_items(root, ns, tenant_id)
    total_trasladados, total_retenidos = _parse_totals_impuestos(root, ns)
    comprobante["total_impuestos_trasladados"] = total_trasladados
    comprobante["total_impuestos_retenidos"] = total_retenidos

    return {"document": comprobante, "parties": parties, "items": items, "taxes": taxes}


def _detect_namespace(root) -> str:
    tag = root.tag
    if CFDI_4_NS in tag:
        return CFDI_4_NS
    return CFDI_3_NS


def _get_uuid(root, ns: str) -> str:
    tfd_ns = "http://www.sat.gob.mx/TimbreFiscalDigital"
    complement = root.find(f"{{{ns}}}Complemento")
    if complement is not None:
        tfd = complement.find(f"{{{tfd_ns}}}TimbreFiscalDigital")
        if tfd is not None:
            return tfd.get("UUID", "")
    return ""


def _get_uso_cfdi(root, ns: str, version: str) -> str | None:
    receptor = root.find(f"{{{ns}}}Receptor")
    if receptor is not None:
        return receptor.get("UsoCFDI")
    return None


def _get_no_certificado_sat(root, ns: str) -> str | None:
    tfd_ns = "http://www.sat.gob.mx/TimbreFiscalDigital"
    complement = root.find(f"{{{ns}}}Complemento")
    if complement is not None:
        tfd = complement.find(f"{{{tfd_ns}}}TimbreFiscalDigital")
        if tfd is not None:
            return tfd.get("NoCertificadoSAT")
    return None


def _get_sello_sat(root, ns: str) -> str | None:
    tfd_ns = "http://www.sat.gob.mx/TimbreFiscalDigital"
    complement = root.find(f"{{{ns}}}Complemento")
    if complement is not None:
        tfd = complement.find(f"{{{tfd_ns}}}TimbreFiscalDigital")
        if tfd is not None:
            return tfd.get("SelloSAT")
    return None


def _parse_parties(root, ns: str, tenant_id: uuid.UUID) -> list[dict]:
    parties = []
    for party_tag, party_type in [("Emisor", "emisor"), ("Receptor", "receptor")]:
        el = root.find(f"{{{ns}}}{party_tag}")
        if el is not None:
            parties.append({
                "tenant_id": tenant_id,
                "party_type": party_type,
                "rfc": el.get("Rfc"),
                "nombre": el.get("Nombre"),
                "regimen_fiscal": el.get("RegimenFiscal"),
                "domicilio_fiscal": el.get("DomicilioFiscalReceptor"),
                "created_at": datetime.now(timezone.utc),
            })
    return parties


def _parse_items(root, ns: str, tenant_id: uuid.UUID) -> tuple[list[dict], list[dict]]:
    items = []
    taxes = []
    conceptos = root.find(f"{{{ns}}}Conceptos")
    if conceptos is None:
        return items, taxes

    for idx, concepto in enumerate(conceptos.findall(f"{{{ns}}}Concepto")):
        item = {
            "tenant_id": tenant_id,
            "item_index": idx,
            "clave_prod_serv": concepto.get("ClaveProdServ"),
            "clave_unidad": concepto.get("ClaveUnidad"),
            "no_identificacion": concepto.get("NoIdentificacion"),
            "descripcion": concepto.get("Descripcion"),
            "cantidad": _decimal_or_none(concepto.get("Cantidad")),
            "valor_unitario": _decimal_or_none(concepto.get("ValorUnitario")),
            "descuento": _decimal_or_none(concepto.get("Descuento")),
            "importe": _decimal_or_none(concepto.get("Importe")),
            "objeto_imp": concepto.get("ObjetoImp"),
            "created_at": datetime.now(timezone.utc),
        }
        items.append(item)

        # Item-level taxes
        impuestos_el = concepto.find(f"{{{ns}}}Impuestos")
        if impuestos_el is not None:
            taxes.extend(_parse_tax_nodes(impuestos_el, ns, tenant_id, item_index=idx))

    return items, taxes


def _parse_tax_nodes(impuestos_el, ns: str, tenant_id: uuid.UUID, item_index: int | None = None) -> list[dict]:
    taxes = []
    for tax_type, container_tag in [("traslado", "Traslados"), ("retencion", "Retenciones")]:
        container = impuestos_el.find(f"{{{ns}}}{container_tag}")
        if container is None:
            continue
        singular = "Traslado" if tax_type == "traslado" else "Retencion"
        for tax_el in container.findall(f"{{{ns}}}{singular}"):
            taxes.append({
                "tenant_id": tenant_id,
                "item_index": item_index,  # mapped later to cfdi_item_id
                "tax_type": tax_type,
                "impuesto": tax_el.get("Impuesto"),
                "tipo_factor": tax_el.get("TipoFactor"),
                "tasa_cuota": _decimal_or_none(tax_el.get("TasaOCuota")),
                "importe": _decimal_or_none(tax_el.get("Importe")),
                "created_at": datetime.now(timezone.utc),
            })
    return taxes


def _parse_totals_impuestos(root, ns: str) -> tuple[Decimal | None, Decimal | None]:
    impuestos = root.find(f"{{{ns}}}Impuestos")
    if impuestos is None:
        return None, None
    return (
        _decimal_or_none(impuestos.get("TotalImpuestosTrasladados")),
        _decimal_or_none(impuestos.get("TotalImpuestosRetenidos")),
    )


def _decimal_or_none(value: str | None) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(value)
    except Exception:
        return None


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    except Exception:
        return None


def run_parse_xml_sync(tenant_id: uuid.UUID, attachment_id: uuid.UUID) -> None:
    """Synchronous entry point for Celery worker. Uses a new DB session."""
    import asyncio
    from app.core.database import AsyncSessionLocal
    from app.core.storage import download_file_bytes
    from app.core.config import settings

    async def _run():
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            from app.db.models.email import EmailAttachment
            from app.db.models.cfdi import CfdiDocument, CfdiParty, CfdiItem, CfdiTax
            from app.services.cfdi_validator import validate_cfdi_xsd
            from datetime import timezone

            result = await db.execute(
                select(EmailAttachment).where(
                    EmailAttachment.id == attachment_id,
                    EmailAttachment.tenant_id == tenant_id,
                )
            )
            attachment = result.scalar_one_or_none()
            if not attachment or not attachment.storage_path:
                return

            xml_bytes = download_file_bytes(attachment.storage_bucket, attachment.storage_path)

            try:
                validate_cfdi_xsd(xml_bytes)
                parsed = parse_cfdi_xml_bytes(xml_bytes, tenant_id)
            except Exception as e:
                doc = CfdiDocument(
                    tenant_id=tenant_id,
                    xml_attachment_id=attachment_id,
                    uuid="INVALID",
                    parse_status="error",
                    parse_error=str(e),
                )
                db.add(doc)
                await db.commit()
                return

            doc_data = parsed["document"]
            doc = CfdiDocument(
                tenant_id=tenant_id,
                xml_attachment_id=attachment_id,
                parse_status="parsed",
                raw_xml_path=attachment.storage_path,
                **doc_data,
            )
            db.add(doc)
            await db.flush()

            for p in parsed["parties"]:
                p["cfdi_document_id"] = doc.id
                db.add(CfdiParty(**p))

            item_id_map = {}
            for item_data in parsed["items"]:
                idx = item_data.pop("item_index")
                item = CfdiItem(cfdi_document_id=doc.id, item_index=idx, **item_data)
                db.add(item)
                await db.flush()
                item_id_map[idx] = item.id

            for tax_data in parsed["taxes"]:
                idx = tax_data.pop("item_index", None)
                tax = CfdiTax(
                    cfdi_document_id=doc.id,
                    cfdi_item_id=item_id_map.get(idx) if idx is not None else None,
                    **tax_data,
                )
                db.add(tax)

            await db.commit()

    asyncio.run(_run())
