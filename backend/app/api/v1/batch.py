import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_role
from app.core.database import get_db
from app.schemas.job import ProcessingJobOut

router = APIRouter()

TenantAuth = Annotated[tuple, Depends(get_current_tenant_role)]


@router.post("/upload-zip", response_model=ProcessingJobOut, status_code=202)
async def upload_zip_for_batch(
    auth: TenantAuth,
    zip_file: UploadFile = File(...),
    template_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Upload a ZIP of CFDIs (XML/PDF). Triggers async batch processing job."""
    user, tenant_id, _ = auth
    from app.services.batch_service import enqueue_zip_batch
    return await enqueue_zip_batch(
        db, tenant_id=tenant_id, user_id=user.id,
        zip_file=zip_file, template_id=template_id,
    )
