# SESSION STATE — 2026-04-09

## Resumen del proyecto

**CFDI Intelligence Platform** — SaaS multi-tenant para ingestión y análisis de facturas CFDI (XML/PDF) desde Gmail.

---

## Estado actual por capa

### Base de datos
- **COMPLETA** — 26 tablas definidas y migradas
- Migration aplicada: `alembic/versions/0dd362f0a932_initial.py`
- Tablas: tenants, users, user_tenant_roles, tenant_settings, email_accounts, sync_jobs, email_messages, email_attachments, cfdi_documents, cfdi_parties, cfdi_items, cfdi_taxes, extraction_templates, processing_jobs, batch_datasets, analytics_snapshots, products_catalog, clients_catalog, suppliers_catalog, export_files, audit_logs + índices por tenant_id
- Driver runtime: `postgresql+asyncpg` | Driver Alembic: `postgresql+psycopg`

### Backend — `backend/app/`

| Módulo | Archivo | Estado |
|---|---|---|
| Config | `core/config.py` | Funcional |
| DB session | `core/database.py` | Funcional |
| Security | `core/security.py` | Funcional |
| Storage (MinIO) | `core/storage.py` | Funcional |
| Auth service | `services/auth_service.py` | Implementado — **BUG CRÍTICO: tokens guardados en UserTenantRole en lugar de EmailAccount (líneas 187-190)** |
| Auth routes | `api/v1/auth.py` | Implementado — `/google/url`, `/callback`, `/refresh` |
| CFDI XML parser | `services/cfdi_xml_parser.py` | Completo + Celery-ready |
| CFDI validator | `services/cfdi_validator.py` | Completo |
| **Gmail service** | `services/gmail_service.py` | **NO EXISTE — bloqueante** |
| **CFDI service** | `services/cfdi_service.py` | **NO EXISTE — bloqueante** |
| Modelos ORM | `db/models/*.py` | Completos |
| Esquemas Pydantic | `schemas/*.py` | Completos |
| Routers Gmail/CFDI | `api/v1/gmail.py`, `api/v1/cfdi.py` | Scaffold — llaman a servicios inexistentes |
| Otros routers | `api/v1/{analytics,batch,exports,jobs,templates,tenants,users}.py` | Scaffold vacío |
| Audit logger | `audit/audit_logger.py` | Funcional |
| Workers Celery | `workers/` | Shells — dependen de gmail_service.py |

### Frontend — `frontend/`

| Módulo | Archivo | Estado |
|---|---|---|
| Login page | `app/(auth)/login/page.tsx` | Funcional |
| OAuth callback | `app/(auth)/callback/page.tsx` | Funcional |
| Auth store | `store/auth-store.ts` | Funcional — Zustand + cookie storage |
| Middleware guard | `middleware.ts` | Funcional — protege rutas privadas |
| Dashboard shell | `app/(dashboard)/page.tsx` | Placeholder sin datos reales |
| API client | `lib/api-client.ts` | Funcional |

### Infraestructura

| Servicio | Estado |
|---|---|
| PostgreSQL 16 | Docker — requiere arrancar desde Windows PowerShell |
| Redis 7 | Docker — requiere arrancar desde Windows PowerShell |
| MinIO | Docker — requiere arrancar desde Windows PowerShell |
| Celery worker | No iniciado — depende de gmail_service.py |

---

## Errores conocidos / pendientes

1. **BUG CRÍTICO — auth_service.py líneas 187-190:** Tokens OAuth se intentan guardar en `UserTenantRole` que no tiene esos campos. Deben ir en `EmailAccount`. Fix descrito en `TODO_NEXT_SESSION.md`.
2. **gmail_service.py no existe** — Todos los endpoints `/api/v1/gmail/*` lanzan `ModuleNotFoundError`.
3. **cfdi_service.py no existe** — Todos los endpoints `/api/v1/cfdi/*` lanzan `ModuleNotFoundError`.
4. **MinIO buckets** — Los buckets deben existir antes del primer sync. No hay auto-creación.
5. **Docker no disponible en WSL** — `docker compose up` debe ejecutarse desde PowerShell en Windows.

---

## Último punto de trabajo (fin de sesión 2026-04-09)

Sesión de **análisis completo** del proyecto. Se identificaron todos los bugs y gaps bloqueantes. No se modificó ningún archivo de código.

Se ejecutó el `SESSION_CLOSE_PROTOCOL.md`. Archivos generados:
- `PROJECT_STATE.md` — estado detallado del sistema
- `TODO_NEXT_SESSION.md` — plan técnico para la próxima sesión
- `DEV_CONTEXT.md` — stack, variables de entorno, comandos
- `START_HERE.md` — guía de retoma rápida
- `AGENT_RULES.md` — reglas para el agente

---

## Comandos para arrancar

**Paso 1 — Infraestructura (desde PowerShell en Windows):**
```powershell
cd C:\Users\Salvador\DyA_Fac_v3
docker compose -f infra/docker-compose.yml up -d
```

**Paso 2 — Backend (desde WSL):**
```bash
cd /mnt/c/Users/Salvador/DyA_Fac_v3/backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

**Paso 3 — Frontend (desde WSL):**
```bash
cd /mnt/c/Users/Salvador/DyA_Fac_v3/frontend
npm run dev
```

**Flujo de login:** `http://localhost:3000` → redirige a `/login` → clic "Iniciar con Google" → Google OAuth → callback en `/callback` → dashboard.
