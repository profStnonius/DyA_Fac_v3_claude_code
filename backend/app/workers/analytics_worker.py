import uuid

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="app.workers.analytics_worker.refresh_analytics_snapshot")
def refresh_analytics_snapshot(self, tenant_id: str, year: int | None = None, month: int | None = None):
    """
    Recompute all analytics KPIs for the given tenant/period and persist to analytics_snapshots.
    Triggered after batch processing or on-demand from the API.
    """
    from app.services.analytics_service import run_analytics_refresh_sync
    run_analytics_refresh_sync(
        tenant_id=uuid.UUID(tenant_id),
        year=year,
        month=month,
    )
