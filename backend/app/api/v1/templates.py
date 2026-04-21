import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_role
from app.core.database import get_db
from app.schemas.template import TemplateCreate, TemplateOut, TemplateUpdate, DetectedFieldsOut

router = APIRouter()

TenantAuth = Annotated[tuple, Depends(get_current_tenant_role)]


@router.post("/detect-fields", response_model=DetectedFieldsOut)
async def detect_fields_from_sample(
    auth: TenantAuth,
    xml_file: UploadFile | None = File(None),
    pdf_file: UploadFile | None = File(None),
):
    """Upload sample CFDI (XML and/or PDF) and get auto-detected fields."""
    user, tenant_id, _ = auth
    from app.services.template_engine import detect_fields_from_sample_files
    return await detect_fields_from_sample_files(xml_file=xml_file, pdf_file=pdf_file)


@router.get("/", response_model=list[TemplateOut])
async def list_templates(auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    user, tenant_id, _ = auth
    from app.services.template_engine import list_templates
    return await list_templates(db, tenant_id=tenant_id)


@router.post("/", response_model=TemplateOut, status_code=201)
async def create_template(payload: TemplateCreate, auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    user, tenant_id, _ = auth
    from app.services.template_engine import create_template
    return await create_template(db, tenant_id=tenant_id, user_id=user.id, payload=payload)


@router.put("/{template_id}", response_model=TemplateOut)
async def update_template(
    template_id: uuid.UUID, payload: TemplateUpdate, auth: TenantAuth, db: AsyncSession = Depends(get_db)
):
    user, tenant_id, _ = auth
    from app.services.template_engine import update_template
    return await update_template(db, tenant_id=tenant_id, template_id=template_id, payload=payload)


@router.delete("/{template_id}", status_code=204)
async def delete_template(template_id: uuid.UUID, auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    user, tenant_id, _ = auth
    from app.services.template_engine import delete_template
    await delete_template(db, tenant_id=tenant_id, template_id=template_id)
