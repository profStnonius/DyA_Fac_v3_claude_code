import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_role
from app.core.database import get_db
from app.schemas.export import ExportFileOut, ExportRequest

router = APIRouter()

TenantAuth = Annotated[tuple, Depends(get_current_tenant_role)]


@router.get("/", response_model=list[ExportFileOut])
async def list_exports(auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    user, tenant_id, _ = auth
    from app.services.export_service import list_export_files
    return await list_export_files(db, tenant_id=tenant_id, user_id=user.id)


@router.post("/generate", response_model=ExportFileOut, status_code=202)
async def generate_export(payload: ExportRequest, auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    """Enqueue report generation (Excel/CSV/PDF). Returns immediately with job status."""
    user, tenant_id, _ = auth
    from app.services.export_service import enqueue_export
    return await enqueue_export(db, tenant_id=tenant_id, user_id=user.id, payload=payload)


@router.get("/{export_id}/download")
async def download_export(export_id: uuid.UUID, auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    """Generate a signed URL and redirect to the file download."""
    user, tenant_id, _ = auth
    from app.services.export_service import get_download_url
    signed_url = await get_download_url(db, tenant_id=tenant_id, export_id=export_id)
    return RedirectResponse(url=signed_url)
