"""Database engine and session utilities (infrastructure layer)."""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlmodel import Session, create_engine

# Read the database URL from the environment variable.
# Fallback to a local SQLite database if the variable is not set.
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Use PostgreSQL
    engine = create_engine(DATABASE_URL, echo=False)
else:
    # Use SQLite as a fallback
    DB_PATH = Path("data/marks.db")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)



def get_session() -> Generator[Session, None, None]:  # FastAPI dependency
    """Yield a database session for a single FastAPI request."""
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

__all__ = ["engine", "get_session", "session_scope"]
