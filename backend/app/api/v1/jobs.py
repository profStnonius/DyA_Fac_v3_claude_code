import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_role
from app.core.database import get_db
from app.schemas.job import ProcessingJobOut, ProcessingJobList

router = APIRouter()

TenantAuth = Annotated[tuple, Depends(get_current_tenant_role)]


@router.get("/", response_model=ProcessingJobList)
async def list_jobs(
    auth: TenantAuth,
    db: AsyncSession = Depends(get_db),
    job_type: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    user, tenant_id, _ = auth
    from app.services.job_service import list_processing_jobs
    return await list_processing_jobs(
        db, tenant_id=tenant_id, job_type=job_type, status=status, page=page, page_size=page_size
    )


@router.get("/{job_id}", response_model=ProcessingJobOut)
async def get_job(job_id: uuid.UUID, auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    user, tenant_id, _ = auth
    from app.services.job_service import get_job_by_id
    return await get_job_by_id(db, tenant_id=tenant_id, job_id=job_id)
