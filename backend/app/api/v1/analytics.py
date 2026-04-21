from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_role
from app.core.database import get_db

router = APIRouter()

TenantAuth = Annotated[tuple, Depends(get_current_tenant_role)]


@router.get("/kpis/summary")
async def get_kpi_summary(
    auth: TenantAuth,
    db: AsyncSession = Depends(get_db),
    year: int | None = None,
    month: int | None = None,
):
    user, tenant_id, _ = auth
    from app.services.analytics_service import get_summary_kpis
    return await get_summary_kpis(db, tenant_id=tenant_id, year=year, month=month)


@router.get("/kpis/top-products")
async def get_top_products(
    auth: TenantAuth,
    db: AsyncSession = Depends(get_db),
    year: int | None = None,
    limit: int = Query(10, ge=1, le=50),
):
    user, tenant_id, _ = auth
    from app.services.analytics_service import get_top_products
    return await get_top_products(db, tenant_id=tenant_id, year=year, limit=limit)


@router.get("/kpis/top-clients")
async def get_top_clients(
    auth: TenantAuth,
    db: AsyncSession = Depends(get_db),
    year: int | None = None,
    limit: int = Query(10, ge=1, le=50),
):
    user, tenant_id, _ = auth
    from app.services.analytics_service import get_top_clients
    return await get_top_clients(db, tenant_id=tenant_id, year=year, limit=limit)


@router.get("/kpis/sales-by-month")
async def get_sales_by_month(
    auth: TenantAuth,
    db: AsyncSession = Depends(get_db),
    year: int | None = None,
):
    user, tenant_id, _ = auth
    from app.services.analytics_service import get_sales_by_month
    return await get_sales_by_month(db, tenant_id=tenant_id, year=year)


@router.post("/refresh", status_code=202)
async def trigger_analytics_refresh(auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    """Dispatch async Celery task to recompute analytics snapshots."""
    user, tenant_id, _ = auth
    from app.services.analytics_service import enqueue_analytics_refresh
    return await enqueue_analytics_refresh(db, tenant_id=tenant_id, user_id=user.id)
