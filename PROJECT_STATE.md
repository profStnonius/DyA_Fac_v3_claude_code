# PROJECT STATE — 2026-04-09

## Arquitectura actual del sistema

**CFDI Intelligence Platform** — SaaS multi-tenant para ingestión y análisis de facturas CFDI (XML/PDF) desde Gmail.

### Stack
- Backend: FastAPI + SQLAlchemy (async) + Alembic + PostgreSQL + Celery + Redis
- Frontend: Next.js (App Router) + TypeScript + Zustand + TanStack Query
- Auth: Google OAuth 2.0 (flujo frontend-redirect)
- Storage: MinIO (S3-compatible) vía boto3
- Workers: Celery + Redis

### Flujo principal (objetivo del sistema)
```
Gmail → sync_email_account (Celery) → EmailAttachment (MinIO) → cfdi_parser (Celery) → CfdiDocument (DB)
```

---

## Estado del Backend (`backend/app/`)

| Módulo | Archivo | Estado |
|---|---|---|
| Config | `core/config.py` | COMPLETO |
| DB session | `core/database.py` | COMPLETO |
| Security (JWT + Fernet) | `core/security.py` | COMPLETO |
| Storage (MinIO/S3) | `core/storage.py` | COMPLETO |
| Logging | `core/logging.py` | COMPLETO |
| Auth service | `services/auth_service.py` | IMPLEMENTADO — tiene bug crítico (ver Errores) |
| CFDI XML parser | `services/cfdi_xml_parser.py` | COMPLETO — incluye `run_parse_xml_sync` para Celery |
| CFDI validator XSD | `services/cfdi_validator.py` | COMPLETO |
| **Gmail service** | `services/gmail_service.py` | **NO EXISTE — bloqueante** |
| **CFDI service** | `services/cfdi_service.py` | **NO EXISTE — bloqueante** |
| ORM models | `db/models/*.py` | COMPLETOS (email, cfdi, user, tenant, analytics, export, job, template) |
| Pydantic schemas | `schemas/*.py` | COMPLETOS (email, cfdi, user, tenant, job, template, export) |
| Auth router | `api/v1/auth.py` | COMPLETO — `/google/url`, `/callback`, `/refresh` |
| Gmail router | `api/v1/gmail.py` | Scaffold — llama a `gmail_service` que no existe |
| CFDI router | `api/v1/cfdi.py` | Scaffold — llama a `cfdi_service` que no existe |
| Otros routers | `api/v1/{analytics,batch,exports,jobs,templates,tenants,users}.py` | Scaffold vacío |
| Audit logger | `audit/audit_logger.py` | COMPLETO |
| Celery app | `workers/celery_app.py` | COMPLETO — config y rutas de queues |
| Worker email sync | `workers/email_sync.py` | Shell — llama a `gmail_service` que no existe |
| Worker CFDI parser | `workers/cfdi_parser.py` | Shell — llama a `cfdi_xml_parser.run_parse_xml_sync` (implementado) |
| Otros workers | `workers/{batch,analytics,export}_worker.py` | Shells vacíos |

### Migraciones
- Migration aplicada: `alembic/versions/0dd362f0a932_initial.py`
- 26 tablas creadas con índices por `tenant_id`

---

## Estado del Frontend (`frontend/`)

| Módulo | Archivo | Estado |
|---|---|---|
| Login page | `app/(auth)/login/page.tsx` | COMPLETO |
| OAuth callback | `app/(auth)/callback/page.tsx` | COMPLETO |
| Auth store (Zustand + cookies) | `store/auth-store.ts` | COMPLETO |
| Middleware de rutas | `middleware.ts` | COMPLETO — protege `/dashboard` |
| Dashboard shell | `app/(dashboard)/page.tsx` | Placeholder — KPIs en cero |
| Dashboard layout | `app/(dashboard)/layout.tsx` | COMPLETO — sidebar + topbar |
| API client | `lib/api-client.ts` | COMPLETO |
| Hooks | `hooks/use-cfdi.ts`, `use-analytics.ts`, `use-jobs.ts` | Scaffold |
| Types | `types/*.ts` | Definidos |
| Componentes | `components/layout/` | Sidebar, Topbar, PageHeader — scaffolds |

---

## Integración OAuth — Qué funciona y qué no

### Funciona
- `GET /api/v1/auth/google/url` → devuelve URL de Google correctamente
- Flujo de redirección frontend → Google → `/callback`
- `POST /api/v1/auth/callback` → intercambia code, crea User + Tenant + UserTenantRole, devuelve JWT
- JWT guardado en cookie `cfdi-auth` (Zustand + cookie storage)
- Middleware protege rutas privadas

### No funciona
- **Bug crítico**: `handle_google_callback` intenta escribir `google_access_token` y `google_refresh_token` en el objeto `UserTenantRole` (líneas 187–190 de `auth_service.py`). Ese modelo NO tiene esos campos → `AttributeError` en runtime. Los tokens de Gmail nunca se persisten. Sin esto, no es posible usar la Gmail API posteriormente.

---

## Errores actuales detectados

### Bug #1 — CRÍTICO: Tokens OAuth mal ubicados
**Archivo:** `backend/app/services/auth_service.py`, líneas 187–190
```python
# CÓDIGO INCORRECTO
if credentials.token:
    role_entry.google_access_token = encrypt_token(credentials.token)  # UserTenantRole no tiene este campo
if credentials.refresh_token:
    role_entry.google_refresh_token = encrypt_token(credentials.refresh_token)  # idem
```
**Fix necesario:** Crear/actualizar un registro `EmailAccount` con los tokens encriptados, asociado al `user.id` y `tenant.id` recién creados.

### Bug #2 — BLOQUEANTE: `gmail_service.py` no existe
El router `api/v1/gmail.py` importa en runtime:
- `from app.services.gmail_service import list_email_accounts`
- `from app.services.gmail_service import disconnect_account`
- `from app.services.gmail_service import trigger_email_sync`
- `from app.services.gmail_service import get_sync_job_status`

Cualquier llamada a estos endpoints lanza `ModuleNotFoundError`.

### Bug #3 — BLOQUEANTE: `cfdi_service.py` no existe
El router `api/v1/cfdi.py` importa en runtime:
- `from app.services.cfdi_service import list_cfdi_documents`
- `from app.services.cfdi_service import get_cfdi_detail`

---

## Último cambio realizado

**En esta sesión (2026-04-09):** Análisis completo del proyecto. Se identificaron los 3 bugs/gaps bloqueantes. El agente **NO modificó ningún archivo** — fue detenido antes de aplicar el primer fix.

**Sesión anterior (2026-04-07):** Se completó el flujo OAuth completo:
- `auth_service.py` creado
- `alembic/env.py` reescrito
- `alembic upgrade head` ejecutado
- `middleware.ts` implementado
- Zustand migrado a cookie storage

---

## Qué estaba intentando resolverse

El agente había propuesto y estaba a punto de ejecutar:
1. **Fix A:** Corregir `auth_service.py` para persistir tokens OAuth en `EmailAccount` en vez de `UserTenantRole`
2. **Fix B:** Crear `services/gmail_service.py` con 6 funciones (list accounts, disconnect, trigger sync, get status, run_email_sync_sync, run_download_attachment_sync)
3. **Fix C:** Crear `services/cfdi_service.py` con list + detail

El agente fue interrumpido al intentar aplicar el Fix A.

---

## Riesgos técnicos actuales

1. **Docker desde Windows** — `docker compose up` debe ejecutarse desde PowerShell en Windows, NO desde WSL. Si los contenedores no están activos, el backend no arranca.
2. **Tokens perdidos en login** — El bug #1 significa que el primer login puede fallar con AttributeError o, si SQLAlchemy lo ignora silenciosamente, los tokens de Gmail nunca se guardan. Conexión Gmail imposible.
3. **Celery sin workers** — Los workers están definidos pero `gmail_service.py` no existe, por lo que importar el módulo de workers fallaría.
4. **MinIO buckets** — Los buckets (`raw-email-attachments`, etc.) deben existir en MinIO antes de que el storage funcione. No hay lógica de auto-creación.
