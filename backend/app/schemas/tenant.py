import uuid
from datetime import datetime

from pydantic import BaseModel


class TenantCreate(BaseModel):
    name: str
    rfc: str | None = None


class TenantOut(BaseModel):
    id: uuid.UUID
    name: str
    rfc: str | None
    plan: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantSettingsOut(BaseModel):
    tenant_id: uuid.UUID
    gmail_sync_schedule: str | None
    notification_email: str | None
    timezone: str
    fiscal_year_start_month: int

    model_config = {"from_attributes": True}


class TenantSettingsUpdate(BaseModel):
    gmail_sync_schedule: str | None = None
    notification_email: str | None = None
    timezone: str | None = None
    fiscal_year_start_month: int | None = None
