"""Database engine and session utilities (infrastructure layer)."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlmodel import Session, create_engine

DB_PATH = Path("data/marks.db")
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
