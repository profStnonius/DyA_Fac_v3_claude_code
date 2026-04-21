import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# Load backend/.env so DATABASE_URL and other settings are available
# before importing the app modules (which call get_settings() at import time).
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Import Base and all models so autogenerate can detect every table.
from app.core.database import Base          # noqa: E402
import app.db.models                        # noqa: E402, F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Build a synchronous URL for Alembic from DATABASE_URL.
# The app uses postgresql+asyncpg:// at runtime; Alembic needs a sync driver.
_async_url = os.environ["DATABASE_URL"]
_sync_url = _async_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)

config.set_main_option("sqlalchemy.url", _sync_url)


def run_migrations_offline() -> None:
    context.configure(
        url=_sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
