from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def _load_dotenv_file(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _build_database_url() -> str:
    existing_url = os.getenv("DATABASE_URL")
    if existing_url:
        return existing_url

    host = os.getenv("DB_HOST")
    if host:
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")
        database = os.getenv("POSTGRES_DB", "postgres")
        port = os.getenv("DB_PORT", "5432")
        auth = f"{user}:{password}@" if password else f"{user}@"
        return f"postgresql+psycopg2://{auth}{host}:{port}/{database}"

    return f"sqlite:///{(BASE_DIR / 'data' / 'marks.db').resolve()}"


_load_dotenv_file(BASE_DIR / ".env")

from src.infrastructure.db import models as _models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = _build_database_url()

config.set_main_option("sqlalchemy.url", database_url)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        version_table="alembic_version",
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
            compare_server_default=True,
            render_as_batch=connection.dialect.name == "sqlite",
            version_table="alembic_version",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()