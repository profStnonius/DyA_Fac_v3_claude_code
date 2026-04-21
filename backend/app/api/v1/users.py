from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_role, require_role
from app.core.database import get_db
from app.schemas.user import UserOut, UserInvite

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_me(auth: Annotated[tuple, Depends(get_current_tenant_role)]):
    user, tenant_id, role = auth
    return user


@router.get("/", response_model=list[UserOut])
async def list_tenant_users(
    auth: Annotated[tuple, Depends(require_role("owner", "admin"))],
    db: AsyncSession = Depends(get_db),
):
    user, tenant_id, _ = auth
    from app.services.tenant_service import list_users_in_tenant
    return await list_users_in_tenant(db, tenant_id=tenant_id)


@router.post("/invite", response_model=UserOut, status_code=201)
async def invite_user(
    payload: UserInvite,
    auth: Annotated[tuple, Depends(require_role("owner", "admin"))],
    db: AsyncSession = Depends(get_db),
):
    user, tenant_id, _ = auth
    from app.services.tenant_service import invite_user_to_tenant
    return await invite_user_to_tenant(db, tenant_id=tenant_id, payload=payload)
