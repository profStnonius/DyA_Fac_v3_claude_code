"""CFDI document query service."""

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.cfdi import CfdiDocument, CfdiParty
from app.schemas.cfdi import CfdiDocumentDetail, CfdiDocumentList, CfdiDocumentOut


async def list_cfdi_documents(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    page: int = 1,
    page_size: int = 50,
    direction: str | None = None,
    rfc: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> CfdiDocumentList:
    base_query = select(CfdiDocument).where(CfdiDocument.tenant_id == tenant_id)

    if direction:
        base_query = base_query.where(CfdiDocument.direction == direction)

    if date_from:
        dt_from = datetime.fromisoformat(date_from).replace(tzinfo=timezone.utc)
        base_query = base_query.where(CfdiDocument.fecha_emision >= dt_from)

    if date_to:
        dt_to = datetime.fromisoformat(date_to).replace(tzinfo=timezone.utc)
        base_query = base_query.where(CfdiDocument.fecha_emision <= dt_to)

    if rfc:
        rfc_subquery = (
            select(CfdiParty.cfdi_document_id)
            .where(CfdiParty.tenant_id == tenant_id, CfdiParty.rfc == rfc)
        )
        base_query = base_query.where(CfdiDocument.id.in_(rfc_subquery))

    count_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    result = await db.execute(
        base_query.order_by(CfdiDocument.fecha_emision.desc())
        .offset(offset)
        .limit(page_size)
    )
    documents = list(result.scalars().all())

    return CfdiDocumentList(
        items=[CfdiDocumentOut.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


async def get_cfdi_detail(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    cfdi_id: uuid.UUID,
) -> CfdiDocumentDetail:
    result = await db.execute(
        select(CfdiDocument)
        .options(
            selectinload(CfdiDocument.parties),
            selectinload(CfdiDocument.items),
        )
        .where(CfdiDocument.id == cfdi_id, CfdiDocument.tenant_id == tenant_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CFDI document not found")

    return CfdiDocumentDetail.model_validate(doc)
