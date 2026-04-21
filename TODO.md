# TODO — Próximos pasos

> Para el plan detallado de la próxima sesión ver: `TODO_NEXT_SESSION.md`

---

## Prioridad 0 — BUG CRÍTICO (bloquea todo lo demás)

- [ ] **Fix `auth_service.py`** — reemplazar escritura de tokens en `UserTenantRole` por `_upsert_email_account`. Ver `TODO_NEXT_SESSION.md` Paso 1.

---

## Prioridad 1 — Epic 3: Gmail Integration

- [ ] Crear `services/gmail_service.py` — list accounts, disconnect, trigger sync, get status, run_email_sync_sync, run_download_attachment_sync
- [ ] Probar `GET /api/v1/gmail/accounts` después del fix de auth
- [ ] Probar `POST /api/v1/gmail/sync` con Celery activo
- [ ] Verificar creación de buckets en MinIO antes del primer sync

---

## Prioridad 2 — Epic 4: CFDI Service

- [ ] Crear `services/cfdi_service.py` — list_cfdi_documents + get_cfdi_detail
- [ ] Probar `GET /api/v1/cfdi/` con datos reales post-sync

---

## Prioridad 3 — Dashboard funcional (mínimo viable)

- [ ] `app/(dashboard)/page.tsx` — KPIs reales desde API
- [ ] `app/(dashboard)/cfdi/` — tabla de CFDIs con filtros
- [ ] `app/(dashboard)/gmail/` — estado de cuentas + botón sync manual
- [ ] Logout: limpiar cookie + redirect a `/login`

---

## Prioridad 4 — Epic 5: PDF Parser + Matching

- [ ] `services/pdf_parser.py` — extracción de texto con PyMuPDF (ya instalado)
- [ ] Matching PDF ↔ XML por UUID CFDI o folio fiscal
- [ ] Actualizar `cfdi_documents.pdf_storage_path`

---

## Prioridad 5 — Epic 6 y 7: Templates + Batch

- [ ] `services/template_service.py` — CRUD plantillas JSON
- [ ] `services/batch_service.py` — generación datasets CSV/Excel
- [ ] Workers correspondientes

---

## Deuda técnica

- [ ] Tests: pytest para servicios críticos (auth, cfdi parser, gmail service)
- [ ] Error handling global en FastAPI (`app/core/exceptions.py`)
- [ ] Rate limiting en endpoints de auth
- [ ] `.env.example` con todas las variables documentadas
- [ ] Auto-creación de buckets MinIO al arrancar backend
- [ ] CI/CD: no configurado

---

## Notas de arquitectura a recordar

- Cada query de negocio DEBE filtrar por `tenant_id`
- Toda operación de escritura DEBE emitir un evento a `audit_logs`
- Archivos binarios van a MinIO — nunca blobs en PostgreSQL
- Celery + Redis para tareas asíncronas (sync Gmail, parsing CFDI, generación datasets)
- Docker debe arrancarse desde Windows PowerShell, no desde WSL
