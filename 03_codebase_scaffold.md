# Codebase Scaffold — CFDI Intelligence Platform

Estructura de directorios del monorepo. Refleja la arquitectura de monolito modular con 8 dominios internos.

```
DyA_Fac_v3/
├── backend/
│   ├── app/
│   │   ├── main.py                        # FastAPI app factory + lifespan
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                    # Dependencies: get_db, get_current_user, get_tenant
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py              # Include all sub-routers
│   │   │       ├── auth.py                # OAuth callback, token refresh
│   │   │       ├── tenants.py             # Tenant CRUD
│   │   │       ├── users.py               # User management
│   │   │       ├── gmail.py               # Connect account, trigger sync
│   │   │       ├── cfdi.py                # List, detail, search CFDIs
│   │   │       ├── templates.py           # Extraction template CRUD
│   │   │       ├── batch.py               # Upload ZIP, trigger batch
│   │   │       ├── jobs.py                # Job status polling
│   │   │       ├── analytics.py           # KPIs, snapshots
│   │   │       └── exports.py             # Download reports
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                  # Pydantic Settings
│   │   │   ├── database.py                # AsyncEngine, AsyncSession, Base
│   │   │   ├── security.py                # JWT, token encryption (Fernet)
│   │   │   ├── logging.py                 # Structured JSON logging
│   │   │   └── storage.py                 # Object storage client (S3/MinIO/Supabase)
│   │   ├── db/
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── base.py                # Declarative base + UUID mixin + tenant mixin
│   │   │       ├── tenant.py              # Tenant, TenantSettings
│   │   │       ├── user.py                # User, UserTenantRole
│   │   │       ├── email.py               # EmailAccount, SyncJob, EmailMessage, EmailAttachment
│   │   │       ├── cfdi.py                # CfdiDocument, CfdiParty, CfdiItem, CfdiTax
│   │   │       ├── template.py            # ExtractionTemplate
│   │   │       ├── job.py                 # ProcessingJob, BatchDataset
│   │   │       ├── analytics.py           # AnalyticsSnapshot, ProductsCatalog, ClientsCatalog, SuppliersCatalog
│   │   │       └── export.py              # ExportFile, AuditLog
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── email.py
│   │   │   ├── cfdi.py
│   │   │   ├── template.py
│   │   │   ├── job.py
│   │   │   ├── analytics.py
│   │   │   └── export.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py            # Google OAuth flow, JWT creation
│   │   │   ├── tenant_service.py          # Tenant onboarding, user-tenant ops
│   │   │   ├── gmail_service.py           # Gmail API wrapper (search, download)
│   │   │   ├── cfdi_xml_parser.py         # lxml CFDI 3.3/4.0 → canonical model
│   │   │   ├── cfdi_pdf_parser.py         # pdfplumber/pymupdf text extraction
│   │   │   ├── cfdi_validator.py          # XSD validation against SAT schemas
│   │   │   ├── cfdi_matcher.py            # PDF↔XML matching logic
│   │   │   ├── template_engine.py         # Apply JSON template to CFDI data
│   │   │   ├── batch_service.py           # ZIP extraction, batch orchestration
│   │   │   ├── normalizer.py              # Canonical dataset normalization
│   │   │   ├── analytics_service.py       # KPI calculations, snapshots
│   │   │   ├── export_service.py          # Excel/CSV/PDF generation (openpyxl)
│   │   │   └── storage_service.py         # Upload/download/signed URLs
│   │   ├── audit/
│   │   │   ├── __init__.py
│   │   │   └── audit_logger.py            # emit_audit_event() — llamado en cada write op
│   │   └── workers/
│   │       ├── __init__.py
│   │       ├── celery_app.py              # Celery app factory + Redis broker config
│   │       ├── email_sync.py              # Tasks: sync_email_account, download_attachment
│   │       ├── cfdi_parser.py             # Tasks: parse_cfdi_xml, parse_cfdi_pdf
│   │       ├── batch_processor.py         # Tasks: process_zip_batch, extract_batch_dataset
│   │       ├── analytics_worker.py        # Tasks: refresh_analytics_snapshot
│   │       └── export_worker.py           # Tasks: generate_excel_report, generate_pdf_report
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── test_cfdi_xml_parser.py
│   │   │   ├── test_cfdi_pdf_parser.py
│   │   │   ├── test_template_engine.py
│   │   │   └── test_normalizer.py
│   │   └── integration/
│   │       ├── test_auth_flow.py
│   │       ├── test_gmail_sync.py
│   │       └── test_batch_processing.py
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── layout.tsx                     # Root layout con providers
│   │   ├── page.tsx                       # Landing / redirect a dashboard
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx             # Login con Google
│   │   │   └── callback/page.tsx          # OAuth callback handler
│   │   └── (dashboard)/
│   │       ├── layout.tsx                 # Dashboard layout con sidebar
│   │       ├── page.tsx                   # Dashboard principal (KPIs resumen)
│   │       ├── gmail/page.tsx             # Cuentas Gmail + disparar sync
│   │       ├── cfdi/
│   │       │   ├── page.tsx               # Listado de CFDIs
│   │       │   └── [id]/page.tsx          # Detalle de CFDI
│   │       ├── templates/
│   │       │   ├── page.tsx               # Listado de plantillas
│   │       │   └── [id]/page.tsx          # Constructor visual de plantilla
│   │       ├── batch/page.tsx             # Upload ZIP + estado de jobs
│   │       ├── analytics/page.tsx         # Dashboard analítico completo
│   │       ├── exports/page.tsx           # Reportes generados + descarga
│   │       └── settings/page.tsx          # Configuración del tenant
│   ├── components/
│   │   ├── ui/                            # Componentes base (Button, Input, Table, etc.)
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Topbar.tsx
│   │   │   └── PageHeader.tsx
│   │   ├── cfdi/
│   │   │   ├── CfdiTable.tsx
│   │   │   ├── CfdiDetail.tsx
│   │   │   └── CfdiStatusBadge.tsx
│   │   ├── templates/
│   │   │   ├── TemplateBuilder.tsx        # Constructor visual con checkboxes
│   │   │   └── TemplateFieldRow.tsx
│   │   ├── jobs/
│   │   │   ├── JobStatusCard.tsx
│   │   │   └── JobProgressBar.tsx
│   │   ├── analytics/
│   │   │   ├── KpiCard.tsx
│   │   │   ├── SalesChart.tsx
│   │   │   ├── TopProductsChart.tsx
│   │   │   ├── TopClientsChart.tsx
│   │   │   └── ProfitHeatmap.tsx
│   │   └── gmail/
│   │       ├── AccountCard.tsx
│   │       └── SyncFiltersForm.tsx
│   ├── lib/
│   │   ├── api-client.ts                  # Axios/fetch wrapper con auth headers
│   │   ├── auth.ts                        # Token storage, refresh logic
│   │   ├── config.ts                      # Env vars
│   │   └── utils.ts                       # Formatters (currency, date, RFC)
│   ├── types/
│   │   ├── cfdi.ts
│   │   ├── template.ts
│   │   ├── analytics.ts
│   │   ├── job.ts
│   │   └── user.ts
│   ├── hooks/
│   │   ├── use-cfdi.ts
│   │   ├── use-jobs.ts
│   │   └── use-analytics.ts
│   ├── store/
│   │   └── auth-store.ts                  # Zustand: user session
│   ├── public/
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── .env.local.example
├── infra/
│   ├── docker-compose.yml                 # Postgres, Redis, MinIO para dev local
│   ├── docker-compose.prod.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.worker
│   └── nginx/
│       └── nginx.conf
├── .env.example                           # Variables globales del monorepo
├── Makefile                               # Comandos de desarrollo
├── 01_ERD_formal.md
├── 02_backlog_tecnico.md
├── 03_codebase_scaffold.md
├── CLAUDE.md
└── README.md
```

## Convenciones de nomenclatura aplicadas

- Archivos y carpetas: `kebab-case`
- Clases Python y componentes React: `PascalCase`
- Variables y funciones Python: `snake_case`
- Variables y funciones TypeScript: `camelCase`
- Constantes: `SCREAMING_SNAKE_CASE`
