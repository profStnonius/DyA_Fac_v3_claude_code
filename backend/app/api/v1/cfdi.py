import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_role
from app.core.database import get_db
from app.schemas.cfdi import CfdiDocumentList, CfdiDocumentDetail

router = APIRouter()

TenantAuth = Annotated[tuple, Depends(get_current_tenant_role)]


@router.get("/", response_model=CfdiDocumentList)
async def list_cfdi(
    auth: TenantAuth,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    direction: str | None = Query(None, pattern="^(received|issued)$"),
    rfc: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    user, tenant_id, _ = auth
    from app.services.cfdi_service import list_cfdi_documents
    return await list_cfdi_documents(
        db, tenant_id=tenant_id, page=page, page_size=page_size,
        direction=direction, rfc=rfc, date_from=date_from, date_to=date_to,
    )


@router.get("/{cfdi_id}", response_model=CfdiDocumentDetail)
async def get_cfdi(cfdi_id: uuid.UUID, auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    user, tenant_id, _ = auth
    from app.services.cfdi_service import get_cfdi_detail
    return await get_cfdi_detail(db, tenant_id=tenant_id, cfdi_id=cfdi_id)
