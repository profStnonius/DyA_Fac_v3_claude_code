import uuid

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="app.workers.cfdi_parser.parse_cfdi_xml")
def parse_cfdi_xml(self, tenant_id: str, attachment_id: str):
    """
    Download XML from storage, parse it into CfdiDocument + related entities,
    validate against SAT XSD, and persist to DB.
    """
    from app.services.cfdi_xml_parser import run_parse_xml_sync
    run_parse_xml_sync(
        tenant_id=uuid.UUID(tenant_id),
        attachment_id=uuid.UUID(attachment_id),
    )


@celery_app.task(bind=True, name="app.workers.cfdi_parser.parse_cfdi_pdf")
def parse_cfdi_pdf(self, tenant_id: str, attachment_id: str, cfdi_document_id: str | None = None):
    """
    Extract text from PDF, attempt matching to a CfdiDocument by UUID/amount/date.
    """
    from app.services.cfdi_pdf_parser import run_parse_pdf_sync
    run_parse_pdf_sync(
        tenant_id=uuid.UUID(tenant_id),
        attachment_id=uuid.UUID(attachment_id),
        cfdi_document_id=uuid.UUID(cfdi_document_id) if cfdi_document_id else None,
    )
