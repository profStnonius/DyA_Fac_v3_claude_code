from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "cfdi-intelligence",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.email_sync",
        "app.workers.cfdi_parser",
        "app.workers.batch_processor",
        "app.workers.analytics_worker",
        "app.workers.export_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Mexico_City",
    enable_utc=True,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_routes={
        "app.workers.email_sync.*": {"queue": "email_sync"},
        "app.workers.cfdi_parser.*": {"queue": "cfdi_parse"},
        "app.workers.batch_processor.*": {"queue": "zip_batch"},
        "app.workers.analytics_worker.*": {"queue": "analytics_refresh"},
        "app.workers.export_worker.*": {"queue": "report_export"},
    },
    task_default_queue="default",
)
