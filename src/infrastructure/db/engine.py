"""Database engine and session utilities (infrastructure layer)."""
from __future__ import annotations

import os
import time
import urllib.parse
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from fastapi import Depends
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlmodel import Session

# Read discrete environment variables
raw_password = os.getenv("DB_PASSWORD")
db_user = os.getenv("DB_USER", "Michael")
db_host = os.getenv("DB_HOST", "postgres_db")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "marks-manager-db")

if raw_password:
    # Dynamically percent-encode the password to ensure valid URI formatting
    safe_password = urllib.parse.quote_plus(raw_password)
    DATABASE_URL = f"postgresql://{db_user}:{safe_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
elif os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
else:
    # Fallback to local SQLite
    DATABASE_URL = None
    db_path = Path("data/marks.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}", echo=False)


def get_session() -> Generator[Session, None, None]:  # FastAPI dependency
    """Yield a SQLAlchemy Session for a single FastAPI request."""
    with Session(engine) as session:
        yield session


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope for scripts and batch jobs."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:  # pragma: no cover
        session.rollback()
        raise
    finally:
        session.close()


def wait_for_database(max_attempts: int = 30, delay_seconds: float = 2.0) -> None:
    """Block until the database is reachable or raise after retries."""
    if not DATABASE_URL or DATABASE_URL.startswith("sqlite"):
        return

    attempt = 0
    last_error: Exception | None = None
    while attempt < max_attempts:
        attempt += 1
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            last_error = exc
            time.sleep(delay_seconds)
        except Exception as exc:
            last_error = exc
            time.sleep(delay_seconds)

    if last_error:
        raise last_error
    raise OperationalError(
        "Database not reachable after retries",
        params=None,
        orig=Exception("Database not reachable after retries"),
    )


__all__ = ["engine", "get_session", "session_scope", "wait_for_database"]