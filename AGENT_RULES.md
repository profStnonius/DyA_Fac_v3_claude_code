# AGENT RULES — Reglas para el agente AI Lead Engineer

## Módulo donde estaba trabajando al detenerse

**`backend/app/services/auth_service.py`** — función `handle_google_callback` (líneas 170–197).
Fix pendiente: reemplazar escritura incorrecta de tokens en `UserTenantRole` por creación de `EmailAccount`.

---

## QUÉ NO DEBE VOLVER A CAMBIAR

### Archivos estables — no tocar sin razón explícita

| Archivo | Razón |
|---|---|
| `backend/app/core/config.py` | Configuración validada y funcional |
| `backend/app/core/database.py` | Sesión async funcionando |
| `backend/app/core/security.py` | JWT + Fernet implementados correctamente |
| `backend/app/core/storage.py` | Cliente MinIO/S3 correcto |
| `backend/app/core/logging.py` | No tocar |
| `backend/app/db/models/*.py` | Todos los modelos validados con migración aplicada |
| `backend/app/schemas/*.py` | Schemas Pydantic completos y coherentes con modelos |
| `backend/app/audit/audit_logger.py` | Implementado y funcional |
| `backend/app/workers/celery_app.py` | Config Celery correcta |
| `backend/alembic/env.py` | Reescrito en sesión anterior — no volver a tocar |
| `frontend/store/auth-store.ts` | Cookie storage configurado correctamente |
| `frontend/middleware.ts` | Protección de rutas implementada |
| `frontend/app/(auth)/login/page.tsx` | Funcional |
| `frontend/app/(auth)/callback/page.tsx` | Funcional |
| `frontend/lib/api-client.ts` | Funcional |

### Decisiones arquitectónicas fijas — no revertir

- **OAuth flow**: Redirección va al frontend (`http://localhost:3000/callback`), NO al backend. El GOOGLE_REDIRECT_URI es siempre el del frontend.
- **DB drivers duales**: Runtime usa `postgresql+asyncpg`, Alembic usa `postgresql+psycopg`. No mezclar.
- **Cookie storage en Zustand**: No cambiar a localStorage — el middleware de Next.js necesita acceso desde Edge runtime.
- **UUIDs como PKs**: No usar enteros secuenciales.
- **Tokens en EmailAccount**: Los tokens OAuth de Gmail se guardan en `email_accounts`, NO en `user_tenant_roles`.
- **Archivos binarios en MinIO**: Nunca guardar blobs en PostgreSQL.
- **tenant_id en cada query**: Toda query de negocio DEBE filtrar por `tenant_id`.
- **audit_logs en escrituras**: Toda operación de escritura DEBE emitir evento de auditoría.

---

## PARTES ESTABLES (no requieren cambios)

- Base de datos completa: 26 tablas, migración aplicada
- Flujo de autenticación (con el fix de tokens pendiente)
- CFDI XML Parser: `cfdi_xml_parser.py` + `cfdi_validator.py` + `xsd/`
- Celery app config y workers shells
- Infraestructura Docker
- Frontend auth (login + callback + store + middleware)

---

## PARTES EN DESARROLLO (trabajo activo)

| Módulo | Estado | Siguiente acción |
|---|---|---|
| `auth_service.py` | Tiene bug — tokens en modelo incorrecto | Fix: usar `_upsert_email_account` |
| `gmail_service.py` | No existe | Crear (ver TODO_NEXT_SESSION.md Paso 2) |
| `cfdi_service.py` | No existe | Crear (ver TODO_NEXT_SESSION.md Paso 3) |
| Dashboard frontend | Placeholder sin datos | Depende de cfdi_service.py |
| Workers Celery | Shells sin implementación real | Dependen de gmail_service.py |

---

## REGLAS DE COMPORTAMIENTO DEL AGENTE

1. **Proponer antes de ejecutar** — Para cualquier cambio en archivos marcados como estables, describir el cambio y esperar confirmación.

2. **No refactorizar código que funciona** — Si un módulo está marcado como estable, no cambiar su estilo, estructura ni nombres salvo que sea estrictamente necesario para el objetivo.

3. **Ciclos pequeños** — Implementar una función a la vez, no ficheros completos de una sola vez sin propuesta previa.

4. **No crear tests por iniciativa propia** — Solo si se solicita explícitamente.

5. **No agregar comentarios ni docstrings** en código que no se esté modificando.

6. **Siempre actualizar SESSION_STATE.md y TODO.md** al final de cada ciclo de trabajo.

7. **No hacer build ni npm install** automáticamente.

8. **No modificar `alembic/versions/`** — Las migraciones existentes están aplicadas. Solo crear nuevas si hay cambios en modelos ORM.

9. **Mantener compatibilidad con el esquema DB** — No cambiar nombres de tablas ni columnas en modelos ORM sin una migración correspondiente.

10. **Docker siempre desde Windows PowerShell** — Nunca intentar ejecutar `docker compose` desde WSL.
