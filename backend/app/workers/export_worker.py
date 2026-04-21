import uuid

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="app.workers.export_worker.generate_excel_report")
def generate_excel_report(self, tenant_id: str, job_id: str, export_file_id: str, dataset_id: str):
    """Generate an Excel file from a batch dataset and upload to storage."""
    from app.services.export_service import run_excel_export_sync
    run_excel_export_sync(
        tenant_id=uuid.UUID(tenant_id),
        job_id=uuid.UUID(job_id),
        export_file_id=uuid.UUID(export_file_id),
        dataset_id=uuid.UUID(dataset_id),
    )


@celery_app.task(bind=True, name="app.workers.export_worker.generate_csv_report")
def generate_csv_report(self, tenant_id: str, job_id: str, export_file_id: str, dataset_id: str):
    """Generate a CSV file from a batch dataset and upload to storage."""
    from app.services.export_service import run_csv_export_sync
    run_csv_export_sync(
        tenant_id=uuid.UUID(tenant_id),
        job_id=uuid.UUID(job_id),
        export_file_id=uuid.UUID(export_file_id),
        dataset_id=uuid.UUID(dataset_id),
    )
