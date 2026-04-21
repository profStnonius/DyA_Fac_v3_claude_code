"""Google OAuth authentication service."""

import asyncio
import hmac
import os
import secrets
import uuid
from datetime import timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from google_auth_oauthlib.flow import Flow

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    encrypt_token,
)
from app.db.models.email import EmailAccount
from app.db.models.tenant import Tenant
from app.db.models.user import User, UserTenantRole
from app.schemas.user import TokenResponse, UserOut

# Allow OAuth over plain HTTP only in local/test environments.
if settings.APP_ENV in {"development", "local", "test"}:
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

OAUTH_STATE_COOKIE_NAME = "cfdi_oauth_state"
OAUTH_STATE_COOKIE_MAX_AGE_SECONDS = 10 * 60

_GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
]

_CLIENT_CONFIG = {
    "web": {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
    }
}


def _make_flow(redirect_uri: str | None = None) -> Flow:
    flow = Flow.from_client_config(
        _CLIENT_CONFIG,
        scopes=_GOOGLE_SCOPES,
        redirect_uri=redirect_uri or settings.GOOGLE_REDIRECT_URI,
    )
    return flow


def generate_oauth_state() -> str:
    return secrets.token_urlsafe(32)


def is_secure_cookie_enabled() -> bool:
    return settings.APP_ENV not in {"development", "local", "test"}


def build_google_auth_url(state: str) -> str:
    flow = _make_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=state,
    )
    return _normalize_google_auth_url(auth_url)


def _normalize_google_auth_url(auth_url: str) -> str:
    """Keep Google-sensitive OAuth params in the exact wire format expected."""
    parts = urlsplit(auth_url)
    query_pairs = parse_qsl(parts.query, keep_blank_values=True)
    normalized_pairs = [
        (key, value)
        for key, value in query_pairs
        if key not in {"include_granted_scopes", "prompt"}
    ]
    normalized_pairs.append(("include_granted_scopes", "true"))
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(normalized_pairs),
            parts.fragment,
        )
    )


def validate_oauth_state(*, received_state: str | None, expected_state: str | None) -> None:
    if not received_state or not expected_state:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing OAuth state",
        )

    if not hmac.compare_digest(received_state, expected_state):
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state",
        )


async def _get_google_user_info(access_token: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


async def _get_or_create_user(db: AsyncSession, google_info: dict[str, Any]) -> User:
    google_sub = google_info["sub"]
    email = google_info["email"]

    result = await db.execute(select(User).where(User.google_sub == google_sub))
    user = result.scalar_one_or_none()
    if user:
        user.avatar_url = google_info.get("picture")
        user.full_name = google_info.get("name")
        return user

    # Fallback: match by email (e.g. user was invited before OAuth)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        user.google_sub = google_sub
        user.avatar_url = google_info.get("picture")
        user.full_name = google_info.get("name")
        return user

    user = User(
        email=email,
        full_name=google_info.get("name"),
        google_sub=google_sub,
        avatar_url=google_info.get("picture"),
        is_active=True,
    )
    db.add(user)
    return user


async def _get_or_create_tenant_role(
    db: AsyncSession, user: User
) -> tuple[Tenant, UserTenantRole]:
    """Return existing tenant association or create a new personal tenant."""
    # Flush to get user.id if newly created
    await db.flush()

    result = await db.execute(
        select(UserTenantRole, Tenant)
        .join(Tenant, Tenant.id == UserTenantRole.tenant_id)
        .where(UserTenantRole.user_id == user.id, Tenant.is_active.is_(True))
        .limit(1)
    )
    row = result.one_or_none()
    if row:
        role_entry, tenant = row
        return tenant, role_entry

    # First login — provision a personal tenant
    domain = user.email.split("@")[1] if "@" in user.email else user.email
    tenant = Tenant(
        name=user.full_name or domain,
        plan="free",
        is_active=True,
    )
    db.add(tenant)
    await db.flush()  # obtain tenant.id

    role_entry = UserTenantRole(
        user_id=user.id,
        tenant_id=tenant.id,
        role="owner",
    )
    db.add(role_entry)
    return tenant, role_entry


async def _upsert_google_email_account(
    db: AsyncSession,
    *,
    user: User,
    tenant: Tenant,
    google_info: dict[str, Any],
    credentials: Any,
) -> EmailAccount:
    email_address = google_info["email"]
    result = await db.execute(
        select(EmailAccount).where(
            EmailAccount.tenant_id == tenant.id,
            EmailAccount.user_id == user.id,
            EmailAccount.email_address == email_address,
        )
    )
    account = result.scalar_one_or_none()
    if account is None:
        account = EmailAccount(
            tenant_id=tenant.id,
            user_id=user.id,
            email_address=email_address,
            is_active=True,
        )
        db.add(account)

    account.is_active = True
    if credentials.token:
        account.google_access_token = encrypt_token(credentials.token)
    if credentials.refresh_token:
        account.google_refresh_token = encrypt_token(credentials.refresh_token)
    if credentials.expiry:
        expiry = credentials.expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        account.token_expiry = expiry
    account.scopes = list(credentials.scopes or _GOOGLE_SCOPES)
    return account


def _build_token_response(
    user: User,
    tenant: Tenant,
    role: str,
) -> TokenResponse:
    access_token = create_access_token(
        subject=str(user.id),
        tenant_id=str(tenant.id),
        extra_claims={"role": role},
    )
    refresh_token = create_refresh_token(
        subject=str(user.id),
        tenant_id=str(tenant.id),
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(user),
        tenant_id=tenant.id,
        role=role,
    )


async def handle_google_callback(
    db: AsyncSession,
    code: str,
    redirect_uri: str,
    state: str,
    expected_state: str | None,
) -> TokenResponse:
    validate_oauth_state(received_state=state, expected_state=expected_state)

    flow = _make_flow(redirect_uri=redirect_uri)
    await asyncio.get_event_loop().run_in_executor(
        None, lambda: flow.fetch_token(code=code)
    )
    credentials = flow.credentials

    google_info = await _get_google_user_info(credentials.token)

    user = await _get_or_create_user(db, google_info)
    tenant, role_entry = await _get_or_create_tenant_role(db, user)
    await _upsert_google_email_account(
        db,
        user=user,
        tenant=tenant,
        google_info=google_info,
        credentials=credentials,
    )

    await db.commit()
    await db.refresh(user)
    await db.refresh(tenant)
    await db.refresh(role_entry)

    return _build_token_response(user, tenant, role_entry.role)


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> TokenResponse:
    import jwt as pyjwt

    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        user_id = uuid.UUID(payload["sub"])
        tenant_id = uuid.UUID(payload["tenant_id"])
    except (pyjwt.PyJWTError, ValueError, KeyError) as exc:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc

    result = await db.execute(
        select(User, UserTenantRole, Tenant)
        .join(UserTenantRole, UserTenantRole.user_id == User.id)
        .join(Tenant, Tenant.id == UserTenantRole.tenant_id)
        .where(
            User.id == user_id,
            UserTenantRole.tenant_id == tenant_id,
            User.is_active.is_(True),
            Tenant.is_active.is_(True),
        )
    )
    row = result.one_or_none()
    if not row:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User or tenant not found",
        )

    user, role_entry, tenant = row
    return _build_token_response(user, tenant, role_entry.role)
