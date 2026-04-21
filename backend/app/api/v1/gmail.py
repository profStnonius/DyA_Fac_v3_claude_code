import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_role, require_role
from app.core.database import get_db
from app.schemas.email import (
    EmailAccountOut,
    GmailAttachmentDownloadOut,
    GmailAttachmentOut,
    GmailMessageOut,
    SyncJobCreate,
    SyncJobOut,
)

router = APIRouter()

TenantAuth = Annotated[tuple, Depends(get_current_tenant_role)]
AdminAuth = Annotated[tuple, Depends(require_role("owner", "admin"))]


@router.get("/accounts", response_model=list[EmailAccountOut])
async def list_gmail_accounts(auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    user, tenant_id, _ = auth
    from app.services.gmail_service import list_email_accounts
    return await list_email_accounts(db, tenant_id=tenant_id)


@router.delete("/accounts/{account_id}", status_code=204)
async def disconnect_gmail_account(account_id: uuid.UUID, auth: AdminAuth, db: AsyncSession = Depends(get_db)):
    user, tenant_id, _ = auth
    from app.services.gmail_service import disconnect_account
    await disconnect_account(db, tenant_id=tenant_id, account_id=account_id)


@router.get("/accounts/{account_id}/messages", response_model=list[GmailMessageOut])
async def list_gmail_messages(
    account_id: uuid.UUID,
    auth: TenantAuth,
    db: AsyncSession = Depends(get_db),
    max_results: int = Query(default=10, ge=1, le=100),
    only_with_attachments: bool = False,
    query: str | None = None,
):
    user, tenant_id, _ = auth
    from app.services.gmail_service import list_recent_messages

    return await list_recent_messages(
        db,
        tenant_id=tenant_id,
        account_id=account_id,
        max_results=max_results,
        only_with_attachments=only_with_attachments,
        query=query,
    )


@router.get(
    "/accounts/{account_id}/messages/{message_id}/attachments",
    response_model=list[GmailAttachmentOut],
)
async def list_gmail_message_attachments(
    account_id: uuid.UUID,
    message_id: str,
    auth: TenantAuth,
    db: AsyncSession = Depends(get_db),
    only_supported: bool = False,
):
    user, tenant_id, _ = auth
    from app.services.gmail_service import list_message_attachments

    return await list_message_attachments(
        db,
        tenant_id=tenant_id,
        account_id=account_id,
        message_id=message_id,
        only_supported=only_supported,
    )


@router.get(
    "/accounts/{account_id}/messages/{message_id}/attachments/{attachment_id}/download",
    response_model=GmailAttachmentDownloadOut,
)
async def download_gmail_message_attachment(
    account_id: uuid.UUID,
    message_id: str,
    attachment_id: str,
    auth: TenantAuth,
    db: AsyncSession = Depends(get_db),
):
    user, tenant_id, _ = auth
    from app.services.gmail_service import download_message_attachment

    return await download_message_attachment(
        db,
        tenant_id=tenant_id,
        account_id=account_id,
        message_id=message_id,
        attachment_id=attachment_id,
    )


@router.post("/sync", response_model=SyncJobOut, status_code=202)
async def trigger_sync(payload: SyncJobCreate, auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    """Dispatch an async email sync job to Celery."""
    user, tenant_id, _ = auth
    from app.services.gmail_service import trigger_email_sync
    return await trigger_email_sync(db, tenant_id=tenant_id, user_id=user.id, payload=payload)


@router.get("/sync/{job_id}", response_model=SyncJobOut)
async def get_sync_status(job_id: uuid.UUID, auth: TenantAuth, db: AsyncSession = Depends(get_db)):
    user, tenant_id, _ = auth
    from app.services.gmail_service import get_sync_job_status
    return await get_sync_job_status(db, tenant_id=tenant_id, job_id=job_id)
