import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None
    avatar_url: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserInvite(BaseModel):
    email: EmailStr
    full_name: str | None = None
    role: str = "analyst"


class GoogleCallbackRequest(BaseModel):
    code: str
    redirect_uri: str
    state: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut
    tenant_id: uuid.UUID
    role: str
