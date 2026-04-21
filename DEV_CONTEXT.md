# DEV CONTEXT — 2026-04-09

## Stack tecnológico y versiones

### Backend
| Tecnología | Versión |
|---|---|
| Python | 3.12 |
| FastAPI | 0.111.x |
| SQLAlchemy (async) | 2.x |
| Alembic | 1.x |
| Celery | 5.4.0 |
| Uvicorn | 0.30.6 |
| google-api-python-client | 2.143.0 |
| google-auth-oauthlib | 1.2.1 |
| boto3 (MinIO/S3) | 1.34.161 |
| PyMuPDF | 1.24.9 |
| lxml | (instalado) |
| pydantic-settings | 2.x |
| cryptography (Fernet) | (instalado) |
| PyJWT | (instalado) |

### Frontend
| Tecnología | Versión |
|---|---|
| Node.js | 18+ |
| Next.js (App Router) | 14.x |
| TypeScript | 5.x |
| Zustand | 4.x |
| TanStack Query | 5.x |
| Tailwind CSS | 3.x |

### Infraestructura
| Servicio | Imagen | Puerto |
|---|---|---|
| PostgreSQL | postgres:16 | 5432 |
| Redis | redis:7 | 6379 |
| MinIO | minio/minio | 9000 (API) / 9001 (Console) |

---

## Variables de entorno necesarias (`backend/.env`)

```env
# App
APP_ENV=development
DEBUG=true
SECRET_KEY=<hex 64 chars>          # openssl rand -hex 32
ALLOWED_ORIGINS=["http://localhost:3000"]

# Database
DATABASE_URL=postgresql+asyncpg://cfdi:cfdi_dev_pass@localhost:5432/cfdi_db

# Redis / Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Google OAuth
GOOGLE_CLIENT_ID=<desde Google Cloud Console credentials.json>
GOOGLE_CLIENT_SECRET=<desde Google Cloud Console credentials.json>
GOOGLE_REDIRECT_URI=http://localhost:3000/callback

# MinIO (Object Storage)
STORAGE_ENDPOINT_URL=http://localhost:9000
STORAGE_ACCESS_KEY=<minio root user>
STORAGE_SECRET_KEY=<minio root password>
STORAGE_REGION=us-east-1
STORAGE_BUCKET_RAW=raw-email-attachments
STORAGE_BUCKET_CFDI=normalized-cfdi
STORAGE_BUCKET_UPLOADS=zip-uploads
STORAGE_BUCKET_REPORTS=generated-reports
STORAGE_BUCKET_TEMP=temp-processing

# JWT
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Fernet (token encryption at rest)
FERNET_KEY=<base64 Fernet key>     # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**IMPORTANTE:** `GOOGLE_REDIRECT_URI` debe ser `http://localhost:3000/callback` tanto aquí como en Google Cloud Console.

---

## Estructura de carpetas relevante

```
DyA_Fac_v3/
├── backend/
│   ├── .venv/                      # virtualenv local
│   ├── .env                        # variables de entorno (no commitear)
│   ├── requirements.txt
│   ├── alembic/
│   │   ├── env.py                  # carga .env, driver sync psycopg
│   │   └── versions/
│   │       └── 0dd362f0a932_initial.py
│   └── app/
│       ├── main.py                 # FastAPI app entry point
│       ├── api/v1/                 # Routers HTTP
│       ├── services/               # Lógica de negocio
│       │   ├── auth_service.py     # OAuth (tiene bug)
│       │   ├── cfdi_xml_parser.py  # Completo
│       │   ├── cfdi_validator.py   # Completo
│       │   ├── gmail_service.py    # FALTA CREAR
│       │   └── cfdi_service.py     # FALTA CREAR
│       ├── db/models/              # SQLAlchemy ORM
│       ├── schemas/                # Pydantic schemas
│       ├── core/                   # Config, DB, Security, Storage, Logging
│       ├── audit/                  # audit_logger.py
│       └── workers/                # Celery tasks
├── frontend/
│   ├── app/
│   │   ├── (auth)/login/
│   │   ├── (auth)/callback/
│   │   └── (dashboard)/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── store/auth-store.ts
│   ├── middleware.ts
│   └── types/
├── infra/
│   └── docker-compose.yml          # PostgreSQL + Redis + MinIO
├── alembic/
├── 01_ERD_formal.md
├── 02_backlog_tecnico.md
├── 03_codebase_scaffold.md
├── CLAUDE.md
├── SESSION_STATE.md
├── TODO.md
└── PROJECT_STATE.md (nuevo)
```

---

## Comandos para iniciar el sistema

### 1. Infraestructura (ejecutar desde PowerShell en Windows, NO desde WSL)
```powershell
cd C:\Users\Salvador\DyA_Fac_v3
docker compose -f infra/docker-compose.yml up -d
```

### 2. Backend (desde WSL)
```bash
cd /mnt/c/Users/Salvador/DyA_Fac_v3/backend
source .venv/bin/activate
uvicorn app.main:app --reload
# Backend disponible en http://localhost:8000
# Docs en http://localhost:8000/docs
```

### 3. Frontend (desde WSL, terminal separada)
```bash
cd /mnt/c/Users/Salvador/DyA_Fac_v3/frontend
npm run dev
# Frontend disponible en http://localhost:3000
```

### 4. Celery worker (desde WSL, terminal separada, con venv activo)
```bash
cd /mnt/c/Users/Salvador/DyA_Fac_v3/backend
source .venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info -Q email_sync,cfdi_parse,default
```

### 5. Migraciones (si hay cambios en modelos)
```bash
cd /mnt/c/Users/Salvador/DyA_Fac_v3/backend
source .venv/bin/activate
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

---

## Endpoints actuales (implementados y funcionales)

| Método | Endpoint | Estado |
|---|---|---|
| GET | `/api/v1/auth/google/url` | FUNCIONAL |
| POST | `/api/v1/auth/callback` | FUNCIONAL (con bug de tokens) |
| POST | `/api/v1/auth/refresh` | FUNCIONAL |
| GET | `/api/v1/gmail/accounts` | ROTO — gmail_service.py no existe |
| DELETE | `/api/v1/gmail/accounts/{id}` | ROTO |
| POST | `/api/v1/gmail/sync` | ROTO |
| GET | `/api/v1/gmail/sync/{job_id}` | ROTO |
| GET | `/api/v1/cfdi/` | ROTO — cfdi_service.py no existe |
| GET | `/api/v1/cfdi/{id}` | ROTO |
| * | `/api/v1/{analytics,batch,exports,jobs,templates,tenants,users}/*` | TODOS ROTOS |

---

## Google Cloud Console — Configuración requerida
- Authorized redirect URIs debe incluir: `http://localhost:3000/callback`
- Scopes habilitados: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
