# DyA_Fac_v3_codex

## 📌 Descripción General

DyA_Fac_v3_codex es una plataforma web para automatizar la descarga, procesamiento y análisis de CFDIs desde Gmail/Google Workspace.

Permite:

* Login con Google (OAuth 2.0)
* Sincronización de correos
* Descarga de XML/PDF
* Parseo de CFDI
* Generación de Excel
* Almacenamiento estructurado

---

## 🏗️ Arquitectura

### Backend

* FastAPI
* Python 3.12
* SQLAlchemy + Alembic
* JWT + OAuth2

### Frontend

* Next.js
* TypeScript
* Tailwind
* Zustand

### Infraestructura

* PostgreSQL
* Redis
* Celery
* MinIO
* Docker

---

## 🔄 Flujo del sistema

1. Login con Google
2. Obtención de tokens
3. Sync de correos
4. Detección de adjuntos
5. Descarga XML/PDF
6. Parseo CFDI
7. Almacenamiento DB
8. Generación Excel

---

## 🔐 Seguridad

* OAuth2 Google
* JWT
* Fernet encryption
* Variables de entorno

---

## 📁 Estructura

DyA_Fac_v3_codex/

* backend/
* frontend/
* infra/
* README.md

---

## ⚙️ Instalación

### Infra

make infra-up

### Backend

cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload

### Frontend

cd frontend
npm install
npm run dev

---

## 🌐 Endpoints

Auth:

* /api/v1/auth/google/url
* /api/v1/auth/callback

Gmail:

* /api/v1/gmail/accounts

CFDI:

* /api/v1/cfdi/

---

## 🧪 Testing

pytest
npx playwright test

---

## 🚀 Estado

Proyecto en desarrollo activo.
