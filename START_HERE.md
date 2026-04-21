# START HERE — Cómo retomar el proyecto mañana

## TL;DR
El sistema tiene OAuth funcionando. El siguiente paso crítico es:
**corregir un bug de 5 líneas en `auth_service.py`**, luego crear dos archivos de servicio. Después de eso, el flujo Gmail → CFDI estará listo para probar.

---

## Paso 1 — Leer primero (2 min)

Leer en este orden:
1. `TODO_NEXT_SESSION.md` — el plan exacto de qué hacer
2. `PROJECT_STATE.md` — para entender los errores detectados

No hace falta releer la arquitectura ni los ERDs — el análisis ya está hecho.

---

## Paso 2 — Levantar infraestructura

**Desde PowerShell en Windows** (NO desde WSL):
```powershell
cd C:\Users\Salvador\DyA_Fac_v3
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml ps
```
Verificar que PostgreSQL (5432), Redis (6379) y MinIO (9000) están `Up`.

**Desde WSL — Backend:**
```bash
cd /mnt/c/Users/Salvador/DyA_Fac_v3/backend
source .venv/bin/activate
uvicorn app.main:app --reload
```
Abrir `http://localhost:8000/docs` — si carga, el backend está OK.

---

## Paso 3 — Atacar el primer problema

**Archivo a modificar:** `backend/app/services/auth_service.py`

**El problema exacto:** La función `handle_google_callback` (línea 170) intenta guardar `google_access_token` en `role_entry` (UserTenantRole). Ese modelo no tiene esos campos.

**El fix:** Ver `TODO_NEXT_SESSION.md` → Paso 1 para el código exacto. En resumen:
- Agregar función `_upsert_email_account`
- En `handle_google_callback`, reemplazar las 4 líneas con tokens por `await _upsert_email_account(...)`

---

## Paso 4 — Crear los dos servicios faltantes

En orden:
1. `backend/app/services/gmail_service.py` — ver `TODO_NEXT_SESSION.md` → Paso 2
2. `backend/app/services/cfdi_service.py` — ver `TODO_NEXT_SESSION.md` → Paso 3

---

## Paso 5 — Probar el flujo

1. Reiniciar backend después de los cambios
2. Abrir `http://localhost:3000`
3. Hacer login con Google
4. Verificar en DB que se creó un `EmailAccount`:
   ```sql
   SELECT * FROM email_accounts;
   ```
5. Probar endpoint: `GET http://localhost:8000/api/v1/gmail/accounts` (con Bearer token)
6. Probar sync: `POST /api/v1/gmail/sync`

---

## Dónde estaba el agente cuando se detuvo

El agente había propuesto los 3 cambios y fue detenido al intentar **aplicar el Fix A** (`auth_service.py`). **Ningún archivo fue modificado en la sesión del 2026-04-09.**

El estado del código es exactamente el del checkpoint anterior (2026-04-07).

---

## Mapa mental del sistema

```
[Google OAuth] ──login──► [auth_service.py] ──crea──► [User + Tenant + EmailAccount*]
                                                                         │
                                                              (*fix pendiente)
                                                                         │
[Frontend] ──trigger sync──► [gmail router] ──llama──► [gmail_service.py*]
                                                              (*crear)
                                                                    │
                                                         [Gmail API] ──descarga──► [MinIO]
                                                                                      │
                                                              [Celery: cfdi_parser] ──►
                                                                                      │
                                                              [cfdi_xml_parser.py] ──►
                                                                                      │
                                                              [DB: cfdi_documents] ──►
                                                                                      │
[Frontend Dashboard] ◄── [cfdi_service.py*] ◄── [cfdi router]
                              (*crear)
```
