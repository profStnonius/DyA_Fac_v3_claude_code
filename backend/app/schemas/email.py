import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EmailAccountOut(BaseModel):
    id: uuid.UUID
    email_address: str
    is_active: bool
    last_sync_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncJobCreate(BaseModel):
    email_account_id: uuid.UUID
    filter_config: dict[str, Any] | None = None
    # filter_config example:
    # {
    #   "from": ["erreka@example.com", "faac@example.com"],
    #   "date_from": "2016-01-01",
    #   "date_to": "2024-12-31",
    #   "has_attachments": true,
    #   "subject_keywords": ["factura", "CFDI"]
    # }


class SyncJobOut(BaseModel):
    id: uuid.UUID
    status: str
    total_messages: int
    processed_messages: int
    failed_messages: int
    started_at: datetime | None
    completed_at: datetime | None
    error_detail: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class GmailAttachmentOut(BaseModel):
    message_id: str
    attachment_id: str
    filename: str
    mime_type: str | None
    size: int | None
    tipo_detectado: str


class GmailAttachmentDownloadOut(GmailAttachmentOut):
    content_base64: str
    sha256: str


class GmailMessageOut(BaseModel):
    id: str
    thread_id: str | None
    subject: str | None
    from_address: str | None
    to_address: str | None
    date: str | None
    snippet: str | None
    label_ids: list[str]
    has_attachments: bool
    attachments: list[GmailAttachmentOut] = Field(default_factory=list)
