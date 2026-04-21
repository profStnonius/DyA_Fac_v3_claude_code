import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ExportRequest(BaseModel):
    export_type: str  # excel / csv / pdf_report
    dataset_id: uuid.UUID | None = None
    template_id: uuid.UUID | None = None
    filters: dict[str, Any] | None = None


class ExportFileOut(BaseModel):
    id: uuid.UUID
    export_type: str
    filename: str
    file_size_bytes: int | None
    expires_at: datetime | None
    download_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
