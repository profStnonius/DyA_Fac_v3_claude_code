from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.user import GoogleCallbackRequest, RefreshTokenRequest, TokenResponse

router = APIRouter()


@router.get("/google/url")
async def get_google_auth_url(response: Response):
    """Return Google OAuth authorization URL for the frontend to redirect to."""
    from app.services.auth_service import (
        OAUTH_STATE_COOKIE_MAX_AGE_SECONDS,
        OAUTH_STATE_COOKIE_NAME,
        build_google_auth_url,
        generate_oauth_state,
        is_secure_cookie_enabled,
    )

    state = generate_oauth_state()
    response.set_cookie(
        key=OAUTH_STATE_COOKIE_NAME,
        value=state,
        max_age=OAUTH_STATE_COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=is_secure_cookie_enabled(),
        samesite="lax",
        path="/api/v1/auth",
    )
    return {"url": build_google_auth_url(state)}


@router.post("/callback", response_model=TokenResponse)
async def google_callback(
    payload: GoogleCallbackRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Exchange Google auth code for platform JWT tokens."""
    return await _exchange_google_callback(
        db=db,
        request=request,
        response=response,
        code=payload.code,
        state=payload.state,
        redirect_uri=payload.redirect_uri,
    )


@router.get("/callback", response_model=TokenResponse)
async def google_callback_redirect(
    request: Request,
    response: Response,
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Google's direct OAuth redirect with query parameters."""
    return await _exchange_google_callback(
        db=db,
        request=request,
        response=response,
        code=code,
        state=state,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )


async def _exchange_google_callback(
    *,
    db: AsyncSession,
    request: Request,
    response: Response,
    code: str,
    state: str,
    redirect_uri: str,
) -> TokenResponse:
    from app.services.auth_service import (
        OAUTH_STATE_COOKIE_NAME,
        handle_google_callback,
        is_secure_cookie_enabled,
    )

    token_response = await handle_google_callback(
        db,
        code=code,
        redirect_uri=redirect_uri,
        state=state,
        expected_state=request.cookies.get(OAUTH_STATE_COOKIE_NAME),
    )
    response.delete_cookie(
        key=OAUTH_STATE_COOKIE_NAME,
        path="/api/v1/auth",
        secure=is_secure_cookie_enabled(),
        samesite="lax",
    )
    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Issue a new access token from a valid refresh token."""
    from app.services.auth_service import refresh_access_token
    return await refresh_access_token(db, refresh_token=payload.refresh_token)
