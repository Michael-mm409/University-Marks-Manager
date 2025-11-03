"""One-off utility to normalize existing Course codes in the database.

By default, trims leading/trailing whitespace. Optionally uppercases codes
with --upper. Safe to run multiple times.

Usage (PowerShell):
  # Trim only
  python -m scripts.normalize_course_codes

  # Trim and uppercase
  python -m scripts.normalize_course_codes --upper

The script uses the same DATABASE_URL/SQLite fallback as the app.
"""
from __future__ import annotations

import argparse
from typing import Optional

from sqlmodel import select

from src.infrastructure.db.engine import session_scope
from src.infrastructure.db.models import Course


def normalize_codes(uppercase: bool = False) -> int:
    """Trim (and optionally uppercase) Course.code values in-place.

    Returns the number of rows updated.
    """
    updated = 0
    with session_scope() as session:
        courses = session.exec(select(Course)).all()
        for c in courses:
            orig: Optional[str] = getattr(c, "code", None)
            if orig is None:
                continue
            new = orig.strip()
            if uppercase:
                new = new.upper()
            if new != orig:
                c.code = new
                session.add(c)
                updated += 1
        if updated:
            # session_scope will commit on exit, but commit early to be explicit
            session.commit()
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize Course.code values (trim and optional uppercase)")
    parser.add_argument("--upper", action="store_true", help="Uppercase all codes after trimming")
    args = parser.parse_args()

    count = normalize_codes(uppercase=args.upper)
    print(f"Normalized {count} course code(s).")


if __name__ == "__main__":
    main()
