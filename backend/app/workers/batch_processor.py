import uuid

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="app.workers.batch_processor.process_zip_batch")
def process_zip_batch(self, tenant_id: str, job_id: str, zip_storage_path: str, template_id: str | None):
    """
    Expand ZIP from storage, identify XML/PDF pairs,
    dispatch parse subtasks, then trigger dataset generation.
    """
    from app.services.batch_service import run_zip_batch_sync
    run_zip_batch_sync(
        tenant_id=uuid.UUID(tenant_id),
        job_id=uuid.UUID(job_id),
        zip_storage_path=zip_storage_path,
        template_id=uuid.UUID(template_id) if template_id else None,
        celery_task=self,
    )


@celery_app.task(bind=True, name="app.workers.batch_processor.generate_batch_dataset")
def generate_batch_dataset(self, tenant_id: str, job_id: str, template_id: str, cfdi_ids: list[str]):
    """
    Apply extraction template to a list of CFDIs and produce a normalized dataset.
    """
    from app.services.batch_service import run_generate_dataset_sync
    run_generate_dataset_sync(
        tenant_id=uuid.UUID(tenant_id),
        job_id=uuid.UUID(job_id),
        template_id=uuid.UUID(template_id),
        cfdi_ids=[uuid.UUID(cid) for cid in cfdi_ids],
        celery_task=self,
    )
