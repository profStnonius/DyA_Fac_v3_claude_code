"""Gmail account, message, and attachment service."""

import asyncio
import base64
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decrypt_token, encrypt_token
from app.db.models.email import EmailAccount, SyncJob
from app.schemas.email import (
    GmailAttachmentDownloadOut,
    GmailAttachmentOut,
    GmailMessageOut,
    SyncJobCreate,
)

GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
GMAIL_SCOPES = [GMAIL_READONLY_SCOPE]


async def list_email_accounts(db: AsyncSession, *, tenant_id: uuid.UUID) -> list[EmailAccount]:
    result = await db.execute(
        select(EmailAccount)
        .where(EmailAccount.tenant_id == tenant_id, EmailAccount.is_active.is_(True))
        .order_by(EmailAccount.created_at.desc())
    )
    return list(result.scalars().all())


async def list_recent_messages(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    account_id: uuid.UUID,
    max_results: int = 10,
    only_with_attachments: bool = False,
    query: str | None = None,
) -> list[GmailMessageOut]:
    account = await _get_email_account(db, tenant_id=tenant_id, account_id=account_id)
    service = await _get_gmail_service(db, account)
    gmail_query = _build_gmail_query(query=query, only_with_attachments=only_with_attachments)
    list_kwargs: dict[str, Any] = {"userId": "me", "maxResults": max_results}
    if gmail_query:
        list_kwargs["q"] = gmail_query

    response = await _execute_gmail_request(
        lambda: service.users().messages().list(**list_kwargs).execute()
    )
    message_refs = response.get("messages", [])
    messages: list[GmailMessageOut] = []
    for message_ref in message_refs:
        raw_message = await _fetch_message(service, message_ref["id"])
        message = _parse_message(raw_message)
        if only_with_attachments and not message.has_attachments:
            continue
        messages.append(message)
    return messages


async def list_message_attachments(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    account_id: uuid.UUID,
    message_id: str,
    only_supported: bool = False,
) -> list[GmailAttachmentOut]:
    account = await _get_email_account(db, tenant_id=tenant_id, account_id=account_id)
    service = await _get_gmail_service(db, account)
    message = _parse_message(await _fetch_message(service, message_id))
    if only_supported:
        return [item for item in message.attachments if item.tipo_detectado in {"pdf", "xml"}]
    return message.attachments


async def download_message_attachment(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    account_id: uuid.UUID,
    message_id: str,
    attachment_id: str,
) -> GmailAttachmentDownloadOut:
    account = await _get_email_account(db, tenant_id=tenant_id, account_id=account_id)
    service = await _get_gmail_service(db, account)
    attachments = _parse_message(await _fetch_message(service, message_id)).attachments
    metadata = next((item for item in attachments if item.attachment_id == attachment_id), None)
    if metadata is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    response = await _execute_gmail_request(
        lambda: service.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()
    )
    raw_content = _decode_gmail_base64(response.get("data", ""))
    payload = metadata.model_dump()
    payload["size"] = metadata.size or len(raw_content)
    return GmailAttachmentDownloadOut(
        **payload,
        content_base64=base64.b64encode(raw_content).decode("ascii"),
        sha256=hashlib.sha256(raw_content).hexdigest(),
    )


async def disconnect_account(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    account_id: uuid.UUID,
) -> None:
    account = await _get_email_account(db, tenant_id=tenant_id, account_id=account_id)
    account.is_active = False
    account.google_access_token = None
    account.google_refresh_token = None
    account.token_expiry = None
    await db.commit()


async def trigger_email_sync(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: SyncJobCreate,
) -> SyncJob:
    account = await _get_email_account(
        db,
        tenant_id=tenant_id,
        account_id=payload.email_account_id,
    )

    job = SyncJob(
        tenant_id=tenant_id,
        email_account_id=account.id,
        triggered_by=user_id,
        status="pending",
        filter_config=payload.filter_config,
        total_messages=0,
        processed_messages=0,
        failed_messages=0,
        created_at=datetime.now(timezone.utc),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    try:
        from app.workers.email_sync import sync_email_account

        sync_email_account.delay(
            str(tenant_id),
            str(account.id),
            str(job.id),
            payload.filter_config or {},
        )
    except Exception as exc:
        job.status = "failed"
        job.error_detail = f"Unable to dispatch email sync job: {exc.__class__.__name__}"
        await db.commit()
        await db.refresh(job)

    return job


async def get_sync_job_status(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    job_id: uuid.UUID,
) -> SyncJob:
    result = await db.execute(
        select(SyncJob).where(SyncJob.tenant_id == tenant_id, SyncJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync job not found")
    return job


def run_email_sync_sync(
    *,
    tenant_id: uuid.UUID,
    email_account_id: uuid.UUID,
    sync_job_id: uuid.UUID,
    filter_config: dict,
    celery_task: object | None = None,
) -> None:
    """Synchronous Celery entry point for a metadata-only Gmail sync."""

    async def _run() -> None:
        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            job = await get_sync_job_status(db, tenant_id=tenant_id, job_id=sync_job_id)
            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            await db.commit()

            try:
                max_results = int(filter_config.get("max_results", 50))
                messages = await list_recent_messages(
                    db,
                    tenant_id=tenant_id,
                    account_id=email_account_id,
                    max_results=max_results,
                    only_with_attachments=bool(filter_config.get("has_attachments", True)),
                    query=filter_config.get("query"),
                )
                job.status = "completed"
                job.total_messages = len(messages)
                job.processed_messages = len(messages)
                job.failed_messages = 0
                job.completed_at = datetime.now(timezone.utc)
            except Exception as exc:
                job.status = "failed"
                job.failed_messages = 1
                job.error_detail = f"Gmail sync failed: {exc.__class__.__name__}"
                job.completed_at = datetime.now(timezone.utc)
            await db.commit()

    asyncio.run(_run())


def run_download_attachment_sync(
    *,
    tenant_id: uuid.UUID,
    attachment_id: uuid.UUID,
) -> None:
    """Placeholder for DB-backed attachment download once EmailAttachment is wired."""
    return None


async def _get_gmail_service(db: AsyncSession, account: EmailAccount) -> Any:
    credentials = _build_credentials(account)
    if not credentials.valid:
        if not credentials.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google consent is missing a refresh token. Reconnect the Gmail account.",
            )
        try:
            await asyncio.to_thread(credentials.refresh, GoogleAuthRequest())
        except RefreshError as exc:
            account.is_active = False
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google token is expired or revoked. Reconnect the Gmail account.",
            ) from exc

        if credentials.token:
            account.google_access_token = encrypt_token(credentials.token)
        if credentials.expiry:
            expiry = credentials.expiry
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            account.token_expiry = expiry
        await db.commit()
        await db.refresh(account)

    return await asyncio.to_thread(
        build,
        "gmail",
        "v1",
        credentials=credentials,
        cache_discovery=False,
    )


def _build_credentials(account: EmailAccount) -> Credentials:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured",
        )
    if not account.google_access_token and not account.google_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gmail account is not connected",
        )

    return Credentials(
        token=decrypt_token(account.google_access_token) if account.google_access_token else None,
        refresh_token=decrypt_token(account.google_refresh_token) if account.google_refresh_token else None,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=account.scopes or GMAIL_SCOPES,
        expiry=_to_google_expiry(account.token_expiry),
    )


async def _fetch_message(service: Any, message_id: str) -> dict[str, Any]:
    return await _execute_gmail_request(
        lambda: service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )


async def _execute_gmail_request(call: Any) -> dict[str, Any]:
    try:
        return await asyncio.to_thread(call)
    except HttpError as exc:
        raise _http_exception_from_google_error(exc) from exc
    except RefreshError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token is expired or revoked. Reconnect the Gmail account.",
        ) from exc


def _http_exception_from_google_error(exc: HttpError) -> HTTPException:
    status_code = getattr(exc.resp, "status", None)
    if status_code == 401:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token is invalid or expired. Reconnect the Gmail account.",
        )
    if status_code == 403:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Google permission denied. Confirm Gmail API access and consent scopes.",
        )
    if status_code == 404:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gmail resource not found")
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Gmail API request failed",
    )


def _parse_message(raw_message: dict[str, Any]) -> GmailMessageOut:
    payload = raw_message.get("payload") or {}
    headers = _headers_to_dict(payload.get("headers", []))
    attachments = _collect_attachments(raw_message.get("id", ""), payload)
    return GmailMessageOut(
        id=raw_message.get("id", ""),
        thread_id=raw_message.get("threadId"),
        subject=headers.get("subject"),
        from_address=headers.get("from"),
        to_address=headers.get("to"),
        date=headers.get("date"),
        snippet=raw_message.get("snippet"),
        label_ids=raw_message.get("labelIds", []),
        has_attachments=bool(attachments),
        attachments=attachments,
    )


def _headers_to_dict(headers: list[dict[str, str]]) -> dict[str, str]:
    return {
        header["name"].lower(): header.get("value", "")
        for header in headers
        if "name" in header
    }


def _collect_attachments(message_id: str, payload: dict[str, Any]) -> list[GmailAttachmentOut]:
    attachments: list[GmailAttachmentOut] = []

    def walk(part: dict[str, Any]) -> None:
        body = part.get("body") or {}
        filename = part.get("filename") or ""
        attachment_id = body.get("attachmentId")
        if attachment_id and filename:
            mime_type = part.get("mimeType")
            attachments.append(
                GmailAttachmentOut(
                    message_id=message_id,
                    attachment_id=attachment_id,
                    filename=filename,
                    mime_type=mime_type,
                    size=body.get("size"),
                    tipo_detectado=_detect_attachment_type(filename=filename, mime_type=mime_type),
                )
            )
        for child in part.get("parts", []) or []:
            walk(child)

    walk(payload)
    return attachments


def _detect_attachment_type(*, filename: str, mime_type: str | None) -> str:
    filename_lower = filename.lower()
    mime_lower = (mime_type or "").lower()
    if filename_lower.endswith(".pdf") or mime_lower == "application/pdf":
        return "pdf"
    if filename_lower.endswith(".xml") or mime_lower in {"application/xml", "text/xml"}:
        return "xml"
    return "otro"


def _decode_gmail_base64(data: str) -> bytes:
    if not data:
        return b""
    padded = data + ("=" * (-len(data) % 4))
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _to_google_expiry(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _build_gmail_query(*, query: str | None, only_with_attachments: bool) -> str | None:
    query_parts = [query.strip()] if query and query.strip() else []
    if only_with_attachments:
        query_parts.append("has:attachment")
    return " ".join(query_parts) or None


async def _get_email_account(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    account_id: uuid.UUID,
) -> EmailAccount:
    result = await db.execute(
        select(EmailAccount).where(
            EmailAccount.tenant_id == tenant_id,
            EmailAccount.id == account_id,
            EmailAccount.is_active.is_(True),
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email account not found")
    return account
