"""One-off migration script: convert existing Assignment.weighted_mark string values to floats where possible.

Run with:
    python scripts/migrate_weighted_mark_to_float.py

This script will:
- Load all assignments from the database
- For each assignment, if weighted_mark is a non-numeric string (e.g., 'S' or 'U') it will set weighted_mark = None
- If weighted_mark is a numeric string, convert to float and persist

Note: This updates values in-place. For schema changes (changing column type in the DB), use Alembic; SQLite may store numeric values in a TEXT column but SQLAlchemy/SQLite will accept numeric inserts.
"""
import os
import sys
from sqlmodel import Session
from sqlalchemy import text

# Make repo root importable when the script is executed from a different working
# directory (e.g., inside a Docker container without the correct CWD). This
# ensures `import src...` works even if the process cwd isn't the project root.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.infrastructure.db.engine import engine
from src.infrastructure.db.models import Assignment


def main():
    # Use raw SQL to avoid SQLModel/ORM type-coercion issues when the DB column type
    # does not match the current ORM model (we may have changed the model to float
    # while the DB column is still varchar). This selects the raw stored values and
    # updates them explicitly.
    with engine.begin() as conn:
        result = conn.exec_driver_sql(
            "SELECT subject_code, assessment, semester_name, year, weighted_mark FROM assignments"
        )
        rows = result.fetchall()
        changed = 0
        for row in rows:
            subject_code, assessment, semester_name, year, val = row
            if val is None:
                continue
            # If already numeric, skip
            if isinstance(val, (float, int)):
                continue
            try:
                new_val = float(val)
                conn.execute(
                    text(
                        "UPDATE assignments SET weighted_mark = :wm WHERE subject_code = :sc AND assessment = :ass AND semester_name = :sem AND year = :yr"
                    ),
                    {"wm": new_val, "sc": subject_code, "ass": assessment, "sem": semester_name, "yr": year},
                )
                changed += 1
            except Exception:
                # Non-numeric -> clear the weighted mark
                conn.execute(
                    text(
                        "UPDATE assignments SET weighted_mark = NULL WHERE subject_code = :sc AND assessment = :ass AND semester_name = :sem AND year = :yr"
                    ),
                    {"sc": subject_code, "ass": assessment, "sem": semester_name, "yr": year},
                )
                changed += 1
        print(f"Processed {len(rows)} assignments, updated {changed} rows.")


if __name__ == '__main__':
    main()
