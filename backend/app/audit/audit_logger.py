import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.export import AuditLog


async def emit_audit_event(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    action: str,
    resource_type: str | None = None,
    resource_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    """Emit an audit log entry. Call this on every write operation."""
    log = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.now(timezone.utc),
    )
    db.add(log)
    # Caller is responsible for committing the session
