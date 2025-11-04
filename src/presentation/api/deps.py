"""Dependency helpers for API layer."""
from __future__ import annotations

from typing import Generator

from sqlmodel import Session

from src.infrastructure.db.engine import engine


def get_session() -> Generator[Session, None, None]:  # FastAPI dependency
    """Yield a database session for a single FastAPI request."""
    with Session(engine) as session:
        yield session


__all__ = ["get_session"]
