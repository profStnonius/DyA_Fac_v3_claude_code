import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ProcessingJobOut(BaseModel):
    id: uuid.UUID
    job_type: str
    status: str
    progress: int
    total_items: int | None
    processed_items: int
    failed_items: int
    output_artifact_id: uuid.UUID | None
    error_detail: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProcessingJobList(BaseModel):
    items: list[ProcessingJobOut]
    total: int
    page: int
    page_size: int
