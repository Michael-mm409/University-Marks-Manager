"""Reset local SQLite database (development only).

- Creates a timestamped backup of data/marks.db if it exists
- Drops all tables and recreates them from current models

Use this if you see OperationalError like:
    sqlite3.OperationalError: no such column: semesters.id

This means your local SQLite schema was created with an older model.
"""
from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

from sqlmodel import SQLModel
from sqlalchemy.engine import Engine

# Make sure the repo root is on sys.path so `import src...` works when running this file directly
try:  # first try normal import
    from src.infrastructure.db.engine import engine
    import src.infrastructure.db.models  # noqa: F401 - ensure models imported
except ModuleNotFoundError:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from src.infrastructure.db.engine import engine  # type: ignore
    import src.infrastructure.db.models  # type: ignore  # noqa: F401


def is_sqlite(e: Engine) -> bool:
    try:
        return e.url.get_backend_name() == "sqlite"
    except Exception:
        return False


def backup_sqlite_file(e: Engine) -> Path | None:
    if not is_sqlite(e):
        return None
    db_path = Path(e.url.database or "data/marks.db")
    if db_path.exists():
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = db_path.with_suffix(f".db.bak.{ts}")
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(db_path, backup)
        return backup
    return None


def reset() -> None:
    if not is_sqlite(engine):
        print("Refusing to reset: DATABASE_URL is not SQLite.")
        sys.exit(2)
    backup = backup_sqlite_file(engine)
    if backup:
        print(f"Backed up SQLite DB to: {backup}")
    else:
        print("No existing SQLite DB to back up; will create fresh tables.")
    # Drop and recreate tables
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("SQLite schema recreated from current models.")


if __name__ == "__main__":
    reset()
