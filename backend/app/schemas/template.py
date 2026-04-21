import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TemplateFieldConfig(BaseModel):
    key: str
    source: str  # xml / pdf
    path: str
    type: str = "string"  # string / number / date / boolean
    required: bool = False
    nullable: bool = True
    format: str | None = None
    transform: str | None = None


class TemplateCreate(BaseModel):
    name: str
    description: str | None = None
    config: dict[str, Any]


class TemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    config: dict[str, Any] | None = None
    is_active: bool | None = None


class TemplateOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    version: int
    is_active: bool
    config: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class DetectedField(BaseModel):
    key: str
    source: str
    path: str
    sample_value: Any | None
    type: str


class DetectedFieldsOut(BaseModel):
    fields: list[DetectedField]
    xml_detected: bool
    pdf_detected: bool
