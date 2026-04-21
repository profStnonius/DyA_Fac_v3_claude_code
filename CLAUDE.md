# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CFDI Intelligence Platform** — a multi-tenant B2B SaaS for ingesting, parsing, and analyzing Mexican fiscal invoices (CFDI XML/PDF) from Gmail. The repo is in early scaffold phase: architecture is fully documented, but implementation is mostly empty directories.

Key documents (read before making architectural decisions):
- `01_ERD_formal.md` — Complete 21-table database schema
- `02_backlog_tecnico.md` — 10 epics with prioritized user stories
- `03_codebase_scaffold.md` — Planned directory structure

## Stack

- **Backend:** FastAPI + SQLAlchemy (async) + Alembic + PostgreSQL + Celery + Redis
- **Frontend:** Next.js (App Router) + TypeScript
- **Auth:** Google OAuth (for Gmail integration)
- **Storage:** Object storage for binary files (PDFs, XMLs) — never store blobs in DB

## Architecture

### Multi-tenancy
All business tables carry a `tenant_id` UUID column. Every query must scope to `tenant_id` to prevent data leakage between tenants.

### Backend structure (`backend/app/`)
```
api/        FastAPI route handlers
services/   Business logic (pure functions, no HTTP concerns)
db/models/  SQLAlchemy ORM models
schemas/    Pydantic request/response schemas
core/       Config, DB session, security, logging
audit/      Audit logging (all write operations must emit audit events)
workers/    Celery task definitions and worker config
```

### Frontend structure (`frontend/`)
```
app/        Next.js App Router pages
components/ Reusable React components
lib/        API client, config helpers
types/      TypeScript type definitions
```

### Key architectural constraints
- UUIDs as primary keys throughout (distributed-system safe)
- Binary files stored in object storage; DB stores only metadata + S3/GCS paths
- All write operations must emit audit log entries (`audit_logs` table)
- Celery workers handle: Gmail sync, CFDI parsing, batch dataset generation
- Template engine is configurable JSON — allows tenants to define custom extraction rules without code changes

## Development Setup

No build tooling exists yet. When scaffolding:

**Backend:**
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Workers:**
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## Epic Priority Order (from backlog)

1. Foundation (monorepo, FastAPI skeleton, DB, Celery)
2. Identity, Roles & Multi-tenancy
3. Google OAuth & Gmail Integration
4. CFDI XML Parser
5. PDF Parser & PDF/XML Matching
6. Configurable JSON Templates
7. Batch Processing & Dataset Generation
8. Commercial Analytics
9. Reporting & Exports
10. Audit, Security & Hardening

### Convenciones

- utiliza kebab-case para nombres de archivos y carpetas
- utiliza PascalCase para nombres de clases y componentes
- utiliza camelCase para nombres de variables y funciones
- utiliza snake_case para nombres de variables y funciones
- utiliza SCREAMING_SNAKE_CASE para constantes
- utiliza kebab-case para nombres de archivos y carpetas
- utiliza PascalCase para nombres de clases y componentes
- utiliza camelCase para nombres de variables y funciones
- utiliza snake_case para nombres de variables y funciones
- utiliza SCREAMING_SNAKE_CASE para constantes

### Consideraciones

- No hagas build en cada cambio

---

## Decisiones técnicas implementadas (2026-04-07)

### Google OAuth — patrón frontend-redirect
El flujo OAuth usa redirección al frontend, NO al backend:
1. Frontend llama `GET /api/v1/auth/google/url` → recibe la URL de Google
2. Usuario aprueba en Google → Google redirige a `http://localhost:3000/callback`
3. Frontend captura el `code` y hace `POST /api/v1/auth/callback` con `{ code, redirect_uri }`
4. Backend intercambia el code por tokens, crea usuario/tenant, devuelve JWT

**`GOOGLE_REDIRECT_URI` debe ser `http://localhost:3000/callback`** — así en `.env` y en Google Cloud Console.

`flow.fetch_token()` es una llamada bloqueante (`requests`). Dentro de FastAPI async se debe envolver:
```python
await asyncio.get_event_loop().run_in_executor(None, lambda: flow.fetch_token(code=code))
```

`OAUTHLIB_INSECURE_TRANSPORT=1` es obligatorio para HTTP en desarrollo — está seteado en `auth_service.py`.

### SQLAlchemy — driver dual
- Runtime (FastAPI): `postgresql+asyncpg://` — driver async
- Alembic (migraciones): `postgresql+psycopg://` — driver sync
- `alembic/env.py` deriva la URL sync automáticamente desde `DATABASE_URL` en `.env`

### Primer login — auto-provisionamiento de tenant
Cuando un usuario hace login por primera vez:
1. Se crea el `User`
2. Se crea un `Tenant` personal con `name = user.full_name`
3. Se crea `UserTenantRole` con `role = "owner"`
4. Se usa `db.flush()` para obtener IDs antes del `db.commit()`

### Auth store — cookie storage en Zustand
El store Zustand usa cookie storage (NO localStorage) porque:
- Next.js Edge middleware no tiene acceso a localStorage
- La cookie `cfdi-auth` es legible desde `middleware.ts` para proteger rutas
- TTL de la cookie: 30 días (igual que `JWT_REFRESH_TOKEN_EXPIRE_DAYS`)
- Formato guardado: `{ state: { accessToken, refreshToken, tenantId, role, user } }`

El middleware en `frontend/middleware.ts` parsea la cookie así:
```typescript
const parsed = JSON.parse(decodeURIComponent(raw));
accessToken = parsed?.state?.accessToken ?? null;
```

### Infraestructura — Docker desde Windows
Docker Desktop no está disponible en el PATH de WSL. Para levantar servicios:
```powershell
# Desde PowerShell en Windows (NO desde WSL)
cd C:\Users\Salvador\DyA_Fac_v3
docker compose -f infra/docker-compose.yml up -d
```
Servicios: PostgreSQL 16 (puerto 5432), Redis 7 (puerto 6379), MinIO (puerto 9000/9001)

### Venv en backend
El proyecto usa `.venv` local (no venv global):
```bash
cd backend
source .venv/bin/activate   # antes de cualquier comando python/alembic/uvicorn
```

### Variables de entorno críticas (backend/.env)
```
DATABASE_URL=postgresql+asyncpg://cfdi:cfdi_dev_pass@localhost:5432/cfdi_db
GOOGLE_CLIENT_ID=<desde credentials.json>
GOOGLE_CLIENT_SECRET=<desde credentials.json>
GOOGLE_REDIRECT_URI=http://localhost:3000/callback
SECRET_KEY=<hex 64 chars>
FERNET_KEY=<base64 Fernet key>
```

### Estado de migraciones
- Migration inicial aplicada: `0dd362f0a932_initial.py`
- 26 tablas creadas con índices por `tenant_id`
- Para re-generar: `alembic revision --autogenerate -m "descripcion"`