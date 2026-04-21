.PHONY: infra-up infra-down backend-install backend-migrate backend-dev worker-dev frontend-install frontend-dev generate-keys

# ── Infrastructure ────────────────────────────────────────────────────────────
infra-up:
	docker compose -f infra/docker-compose.yml up -d

infra-down:
	docker compose -f infra/docker-compose.yml down

# ── Backend ───────────────────────────────────────────────────────────────────
backend-install:
	cd backend && pip install -r requirements-dev.txt

backend-migrate:
	cd backend && alembic upgrade head

backend-dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ── Workers ───────────────────────────────────────────────────────────────────
worker-dev:
	cd backend && celery -A app.workers.celery_app worker --loglevel=info \
		-Q email_sync,cfdi_parse,zip_batch,analytics_refresh,report_export,default

# ── Frontend ──────────────────────────────────────────────────────────────────
frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

# ── Dev shortcuts ─────────────────────────────────────────────────────────────
dev: infra-up
	@echo "Infrastructure started. Run backend-dev and frontend-dev in separate terminals."

# ── Utilities ─────────────────────────────────────────────────────────────────
generate-keys:
	@echo "SECRET_KEY:"
	@python -c "import secrets; print(secrets.token_hex(32))"
	@echo "\nFERNET_KEY:"
	@python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

generate-migration:
	cd backend && alembic revision --autogenerate -m "$(name)"
