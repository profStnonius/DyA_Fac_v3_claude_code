from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_role, require_role
from app.core.database import get_db
from app.schemas.tenant import TenantOut, TenantCreate, TenantSettingsOut, TenantSettingsUpdate

router = APIRouter()


@router.post("/", response_model=TenantOut, status_code=201)
async def create_tenant(payload: TenantCreate, db: AsyncSession = Depends(get_db)):
    """Onboard a new tenant (public — used during registration)."""
    from app.services.tenant_service import create_tenant
    return await create_tenant(db, payload=payload)


@router.get("/me", response_model=TenantOut)
async def get_my_tenant(
    auth: Annotated[tuple, Depends(get_current_tenant_role)],
    db: AsyncSession = Depends(get_db),
):
    user, tenant_id, _ = auth
    from app.services.tenant_service import get_tenant_by_id
    return await get_tenant_by_id(db, tenant_id=tenant_id)


@router.get("/me/settings", response_model=TenantSettingsOut)
async def get_tenant_settings(
    auth: Annotated[tuple, Depends(get_current_tenant_role)],
    db: AsyncSession = Depends(get_db),
):
    user, tenant_id, _ = auth
    from app.services.tenant_service import get_tenant_settings
    return await get_tenant_settings(db, tenant_id=tenant_id)


@router.put("/me/settings", response_model=TenantSettingsOut)
async def update_tenant_settings(
    payload: TenantSettingsUpdate,
    auth: Annotated[tuple, Depends(require_role("owner", "admin"))],
    db: AsyncSession = Depends(get_db),
):
    user, tenant_id, _ = auth
    from app.services.tenant_service import update_tenant_settings
    return await update_tenant_settings(db, tenant_id=tenant_id, payload=payload)
