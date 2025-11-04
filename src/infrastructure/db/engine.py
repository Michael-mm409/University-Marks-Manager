"""Database engine and session utilities (infrastructure layer)."""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlmodel import Session, create_engine
from fastapi import Depends

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
    """
    Yield a SQLAlchemy Session for a single FastAPI request.

    Designed to be used as a FastAPI dependency (e.g., Depends(get_session)).
    A new Session is created from the module-level engine and yielded to the
    request handler. The Session is created within a context manager so it is
    automatically closed when the request scope ends.

    Yields:
        sqlalchemy.orm.Session: an active database session bound to the configured engine.

    Notes:
        - This dependency does not perform commits or rollbacks; route handlers
          should manage transactions as appropriate.
        - Exceptions raised in the request handler will propagate, but the session
          will still be closed by the context manager.

    Example:

        def read_items(db: Session = Depends(get_session)):
            return db.query(Item).all()
    """
    with Session(engine) as session:
        yield session


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope for scripts and batch jobs.

    Yields a configured SQLAlchemy Session bound to the module-level engine. The
    intended usage is as a context manager: on normal exit the session's
    transaction is committed; if an exception occurs the transaction is rolled
    back and the original exception is re-raised. The session is closed in all
    cases to ensure resources are released.

    Returns:
        Generator[Session, None, None]: a generator that yields an active Session.

    Behavior:
        - Yield an active Session to the caller.
        - On successful completion: commit the transaction.
        - On exception: roll back the transaction and re-raise the exception.
        - Always close the session at the end to free connections/resources.

    Notes:
        - Designed for short-lived transactional scopes (scripts, batch jobs,
          CLI commands). For long-lived or highly concurrent usage, prefer
          explicit session management appropriate to your application's
          concurrency model.
        - The function is intended to be used as a context manager (e.g.
          "with session_scope() as session: ...") when decorated with
          contextlib.contextmanager in the surrounding module.
    """
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
