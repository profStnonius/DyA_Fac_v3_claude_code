# TODO — PRÓXIMA SESIÓN

## Problema a resolver primero

**Bug crítico en `auth_service.py`** — tokens OAuth guardados en modelo incorrecto.
Sin este fix, la integración Gmail es imposible.

---

## Pasos técnicos en orden de implementación

### Paso 1 — Fix `auth_service.py` (15 min)
**Archivo:** `backend/app/services/auth_service.py`

Reemplazar las líneas 183–192 de `handle_google_callback`:

```python
# ELIMINAR esto (UserTenantRole no tiene estos campos):
if credentials.token:
    role_entry.google_access_token = encrypt_token(credentials.token)
if credentials.refresh_token:
    role_entry.google_refresh_token = encrypt_token(credentials.refresh_token)

# REEMPLAZAR con esto (crear/actualizar EmailAccount):
await _upsert_email_account(db, user=user, tenant=tenant, credentials=credentials)
```

Agregar función `_upsert_email_account` en el mismo archivo:
```python
async def _upsert_email_account(db, user, tenant, credentials):
    from app.db.models.email import EmailAccount
    from datetime import timezone

    result = await db.execute(
        select(EmailAccount).where(
            EmailAccount.user_id == user.id,
            EmailAccount.tenant_id == tenant.id,
            EmailAccount.email_address == user.email,
        )
    )
    account = result.scalar_one_or_none()
    if account is None:
        account = EmailAccount(
            user_id=user.id,
            tenant_id=tenant.id,
            email_address=user.email,
            is_active=True,
        )
        db.add(account)

    if credentials.token:
        account.google_access_token = encrypt_token(credentials.token)
    if credentials.refresh_token:
        account.google_refresh_token = encrypt_token(credentials.refresh_token)
    if getattr(credentials, 'expiry', None):
        account.token_expiry = credentials.expiry.replace(tzinfo=timezone.utc)
    if getattr(credentials, 'scopes', None):
        account.scopes = list(credentials.scopes)
```

---

### Paso 2 — Crear `gmail_service.py` (45 min)
**Archivo nuevo:** `backend/app/services/gmail_service.py`

Funciones requeridas por el router (`api/v1/gmail.py`):

| Función | Descripción |
|---|---|
| `list_email_accounts(db, tenant_id)` | Query `EmailAccount` filtrado por `tenant_id` |
| `disconnect_account(db, tenant_id, account_id)` | Soft-delete: `is_active = False` |
| `trigger_email_sync(db, tenant_id, user_id, payload)` | Crear `SyncJob` → dispatch Celery `sync_email_account` |
| `get_sync_job_status(db, tenant_id, job_id)` | Query `SyncJob` por `id + tenant_id` |
| `run_email_sync_sync(...)` | Lógica Gmail API sync (llamada desde Celery worker) |
| `run_download_attachment_sync(...)` | Download attachment bytes + upload MinIO |

Dependencias para Gmail API:
```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
```

Patrón para construir el cliente Gmail:
```python
creds = Credentials(
    token=decrypt_token(account.google_access_token),
    refresh_token=decrypt_token(account.google_refresh_token),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    scopes=account.scopes,
)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    account.google_access_token = encrypt_token(creds.token)
service = build('gmail', 'v1', credentials=creds)
```

Query string de Gmail desde `filter_config`:
```python
# filter_config = { "from": ["x@y.com"], "date_from": "2024-01-01", "has_attachments": true }
parts = []
if filter_config.get("has_attachments"):
    parts.append("has:attachment")
for sender in filter_config.get("from", []):
    parts.append(f"from:{sender}")
if date_from := filter_config.get("date_from"):
    parts.append(f"after:{date_from.replace('-', '/')}")
if date_to := filter_config.get("date_to"):
    parts.append(f"before:{date_to.replace('-', '/')}")
query = " ".join(parts) or "has:attachment"
```

Para descargar adjunto desde Gmail API:
```python
import base64
att_data = service.users().messages().attachments().get(
    userId='me', messageId=gmail_msg_id, id=gmail_att_id
).execute()
file_bytes = base64.urlsafe_b64decode(att_data['data'])
```

---

### Paso 3 — Crear `cfdi_service.py` (20 min)
**Archivo nuevo:** `backend/app/services/cfdi_service.py`

Funciones requeridas por `api/v1/cfdi.py`:

```python
async def list_cfdi_documents(db, tenant_id, page, page_size, direction, rfc, date_from, date_to):
    # SELECT + filtros por tenant_id, direction, fecha_emision
    # Si rfc: JOIN con CfdiParty WHERE rfc = ?
    # LIMIT + OFFSET para paginación
    # Devuelve CfdiDocumentList

async def get_cfdi_detail(db, tenant_id, cfdi_id):
    # SELECT CfdiDocument con joined parties e items
    # Validar tenant_id para prevenir data leakage
    # Raise 404 si no existe
    # Devuelve CfdiDocumentDetail
```

---

### Paso 4 — Verificar MinIO buckets (10 min)
Antes de probar sync, verificar que los buckets existen en MinIO:
- `raw-email-attachments`
- `normalized-cfdi`

Acceder a MinIO console: `http://localhost:9001` (user: ver `.env`)

O crear los buckets programáticamente en `core/storage.py` con `client.create_bucket(Bucket=name)`.

---

### Paso 5 — Probar flujo completo (30 min)
1. Arrancar infraestructura (Docker desde Windows PowerShell)
2. Arrancar backend: `uvicorn app.main:app --reload`
3. Arrancar frontend: `npm run dev`
4. Login con Google → verificar que se crea `EmailAccount` en DB
5. `GET /api/v1/gmail/accounts` → debe retornar la cuenta conectada
6. `POST /api/v1/gmail/sync` → debe crear SyncJob
7. Si Celery está activo → verificar que los adjuntos se descargan

---

## Dependencias pendientes

- MinIO buckets deben existir antes del primer sync
- Redis debe estar activo para Celery (Docker)
- Credenciales Google OAuth en `backend/.env` deben tener scope `gmail.readonly`
- Si el primer login ya ocurrió sin el fix → el `EmailAccount` no se creó → necesario volver a hacer login después del fix

---

## Archivos que deberán modificarse

| Archivo | Acción |
|---|---|
| `backend/app/services/auth_service.py` | Modificar `handle_google_callback` — fix tokens |
| `backend/app/services/gmail_service.py` | CREAR nuevo |
| `backend/app/services/cfdi_service.py` | CREAR nuevo |

---

## Orden recomendado

1. auth_service.py fix (desbloquea todo lo demás)
2. gmail_service.py (ruta crítica hacia el objetivo principal)
3. cfdi_service.py (necesario para ver resultados del parsing)
4. Probar end-to-end con Celery activo
5. Dashboard frontend con datos reales
