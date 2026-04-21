import uuid

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="app.workers.email_sync.sync_email_account")
def sync_email_account(self, tenant_id: str, email_account_id: str, sync_job_id: str, filter_config: dict):
    """
    Sync emails from a Gmail account matching the given filters.
    For each email with attachments, dispatches download_attachment subtasks.
    """
    from app.services.gmail_service import run_email_sync_sync
    run_email_sync_sync(
        tenant_id=uuid.UUID(tenant_id),
        email_account_id=uuid.UUID(email_account_id),
        sync_job_id=uuid.UUID(sync_job_id),
        filter_config=filter_config,
        celery_task=self,
    )


@celery_app.task(bind=True, name="app.workers.email_sync.download_attachment")
def download_attachment(self, tenant_id: str, attachment_id: str):
    """Download a single email attachment and upload it to object storage."""
    from app.services.gmail_service import run_download_attachment_sync
    run_download_attachment_sync(
        tenant_id=uuid.UUID(tenant_id),
        attachment_id=uuid.UUID(attachment_id),
    )
