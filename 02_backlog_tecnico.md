# Backlog Técnico — CFDI Intelligence Platform

10 épicas en orden de prioridad de implementación. Cada épica incluye sus user stories técnicas.

---

## Épica 1 — Foundation (Monorepo, FastAPI skeleton, DB, Celery)

**Goal:** Tener un entorno funcional de desarrollo con la plataforma básica corriendo.

| ID | Historia | Prioridad |
|---|---|---|
| E1-01 | Crear estructura de directorios del monorepo (backend/frontend/infra) | Alta |
| E1-02 | Configurar FastAPI con health check, CORS, lifespan | Alta |
| E1-03 | Configurar SQLAlchemy async + Alembic con migración inicial | Alta |
| E1-04 | Configurar Celery + Redis con tarea de prueba | Alta |
| E1-05 | Configurar docker-compose para desarrollo local (postgres, redis, minio) | Alta |
| E1-06 | Configurar variables de entorno con pydantic-settings | Alta |
| E1-07 | Configurar logging estructurado (JSON) | Media |
| E1-08 | Crear Makefile con comandos de desarrollo | Baja |

---

## Épica 2 — Identity, Roles & Multi-tenancy

**Goal:** Sistema de autenticación JWT y aislamiento por tenant.

| ID | Historia | Prioridad |
|---|---|---|
| E2-01 | Modelo de datos: users, tenants, user_tenant_roles, tenant_settings | Alta |
| E2-02 | Endpoint de registro de tenant (onboarding) | Alta |
| E2-03 | Middleware de tenant_id en todas las requests autenticadas | Alta |
| E2-04 | Dependency de FastAPI para extraer tenant_id + user_id del JWT | Alta |
| E2-05 | RBAC: decoradores/deps para verificar rol (owner/admin/analyst/viewer) | Alta |
| E2-06 | Endpoint de gestión de usuarios del tenant (invitar, desactivar) | Media |
| E2-07 | Migración Alembic para tablas de identidad | Alta |

---

## Épica 3 — Google OAuth & Gmail Integration

**Goal:** Conectar cuentas Gmail y sincronizar correos con adjuntos CFDI.

| ID | Historia | Prioridad |
|---|---|---|
| E3-01 | Flujo OAuth 2.0 con Google (authorization URL + callback) | Alta |
| E3-02 | Almacenar/refrescar tokens cifrados en email_accounts | Alta |
| E3-03 | Endpoint para listar cuentas Gmail conectadas | Alta |
| E3-04 | Tarea Celery: email_sync — buscar correos por filtros (remitente, fecha, adjuntos) | Alta |
| E3-05 | Tarea Celery: attachment_download — descargar PDF/XML adjuntos a storage | Alta |
| E3-06 | Guardar email_messages y email_attachments en DB | Alta |
| E3-07 | Endpoint para disparar sync job y consultar su estado | Alta |
| E3-08 | Procesamiento histórico: soporte para rangos de hasta 8 años | Media |
| E3-09 | Scopes mínimos: gmail.readonly | Alta |

---

## Épica 4 — CFDI XML Parser

**Goal:** Parsear XMLs CFDI 3.3 y 4.0 a modelo canónico en DB.

| ID | Historia | Prioridad |
|---|---|---|
| E4-01 | Parser XML CFDI 3.3 → modelo canónico (cfdi_documents, cfdi_parties, cfdi_items, cfdi_taxes) | Alta |
| E4-02 | Parser XML CFDI 4.0 → modelo canónico | Alta |
| E4-03 | cfdi_validator: validar estructura contra esquema SAT (XSD) | Alta |
| E4-04 | Tarea Celery: cfdi_parse — leer XML desde storage y guardar en DB | Alta |
| E4-05 | Manejo de errores: CFDIs inválidos, corrompidos, duplicados (UUID único) | Alta |
| E4-06 | Clasificación automática: recibida vs emitida por RFC del tenant | Alta |
| E4-07 | Endpoint REST: listar CFDIs con filtros (fecha, RFC, tipo, estado) | Alta |
| E4-08 | Endpoint REST: detalle de un CFDI (con conceptos e impuestos) | Alta |

---

## Épica 5 — PDF Parser & PDF/XML Matching

**Goal:** Extraer datos de PDFs de facturas y vincularlos al CFDI XML correspondiente.

| ID | Historia | Prioridad |
|---|---|---|
| E5-01 | pdf_parser: extraer texto y tablas con pdfplumber | Alta |
| E5-02 | field_mapper: detectar campos comunes (RFC, UUID, total, fecha) en texto extraído | Alta |
| E5-03 | Algoritmo de matching PDF↔XML por UUID, nombre de archivo, fecha e importe | Alta |
| E5-04 | Endpoint: obtener tabla de comparación Campo XML | Campo PDF | Coincidencia | Media |
| E5-05 | Manejo de PDFs con OCR fallback (pymupdf) para PDFs escaneados | Baja |
| E5-06 | Guardar ruta del PDF vinculado en cfdi_documents.pdf_attachment_id | Alta |

---

## Épica 6 — Configurable JSON Templates

**Goal:** Permitir al usuario definir visualmente qué campos extraer y guardar como plantilla JSON versionada.

| ID | Historia | Prioridad |
|---|---|---|
| E6-01 | Endpoint: subir CFDI muestra (XML y/o PDF) y obtener campos detectados | Alta |
| E6-02 | Endpoint CRUD para extraction_templates (crear, listar, versionar, activar) | Alta |
| E6-03 | template_engine: aplicar plantilla JSON a un CFDI y retornar fila de datos | Alta |
| E6-04 | Validación de plantillas: paths inválidos, campos obligatorios faltantes | Media |
| E6-05 | Frontend: constructor visual de plantilla con checkboxes por campo | Alta |
| E6-06 | Soporte para transformaciones en plantilla (format_date, round, uppercase) | Baja |

---

## Épica 7 — Batch Processing & Dataset Generation

**Goal:** Procesar miles de CFDIs masivamente y generar datasets Excel/CSV.

| ID | Historia | Prioridad |
|---|---|---|
| E7-01 | Endpoint: subir ZIP de CFDIs para procesamiento batch | Alta |
| E7-02 | Tarea Celery: zip_batch — expandir ZIP, identificar XML/PDF, lanzar subtareas de parsing | Alta |
| E7-03 | normalizer: producir dataset canónico aplicando plantilla a lote de CFDIs | Alta |
| E7-04 | Generador Excel con openpyxl: columnas configurables por plantilla | Alta |
| E7-05 | Generador CSV | Media |
| E7-06 | Tarea Celery: report_export — generar archivo y subirlo a storage | Alta |
| E7-07 | Endpoint: consultar estado de processing_job y descargar resultado | Alta |
| E7-08 | Performance target: 10,000 CFDIs en menos de 2 minutos (workers paralelos) | Alta |

---

## Épica 8 — Commercial Analytics

**Goal:** Motor analítico para KPIs comerciales y financieros.

| ID | Historia | Prioridad |
|---|---|---|
| E8-01 | Tarea Celery: analytics_refresh — calcular snapshots por tenant y periodo | Alta |
| E8-02 | KPIs: top 10 productos, top clientes, ventas por mes/año, compras por periodo | Alta |
| E8-03 | Cálculo de utilidad: ventas - costos (con products_catalog.cost_reference) | Alta |
| E8-04 | Endpoints REST: KPIs con filtros (cliente, producto, periodo, proveedor) | Alta |
| E8-05 | Materialized views o tablas agregadas para performance analítica | Media |
| E8-06 | Tendencias: variación mensual/anual YoY y MoM | Media |
| E8-07 | clients_catalog y suppliers_catalog auto-poblados desde CFDIs parseados | Media |

---

## Épica 9 — Reporting & Exports

**Goal:** Dashboards visuales y exportación de reportes.

| ID | Historia | Prioridad |
|---|---|---|
| E9-01 | Frontend: dashboard principal con KPIs resumen | Alta |
| E9-02 | Frontend: gráficas de barras, líneas, pie y heatmaps (Recharts/ECharts) | Alta |
| E9-03 | Frontend: filtros dinámicos por cliente, producto, periodo, proveedor | Alta |
| E9-04 | Frontend: bandeja de sync jobs con estado en tiempo real (polling o WebSocket) | Media |
| E9-05 | Endpoint: generar PDF de reporte ejecutivo (con weasyprint o similar) | Baja |
| E9-06 | URLs firmadas de descarga con expiración (15 min) | Alta |
| E9-07 | Frontend: pantalla de constructor de plantilla JSON | Alta |

---

## Épica 10 — Audit, Security & Hardening

**Goal:** Seguridad, observabilidad y preparación para producción.

| ID | Historia | Prioridad |
|---|---|---|
| E10-01 | audit_logs: emitir evento en toda operación de escritura | Alta |
| E10-02 | Cifrado de tokens OAuth en reposo (Fernet/AES-256) | Alta |
| E10-03 | Rate limiting por tenant en API | Media |
| E10-04 | Validación de tamaño y tipo MIME en uploads | Alta |
| E10-05 | Expiración automática de export_files y limpieza de storage | Media |
| E10-06 | Tests de integración para flujo completo Gmail → CFDI → Dataset | Alta |
| E10-07 | Tests unitarios para parsers XML y PDF | Alta |
| E10-08 | Configuración de producción: HTTPS, secrets manager, health checks | Alta |
| E10-09 | Documentación API con OpenAPI/Swagger auto-generada por FastAPI | Baja |
