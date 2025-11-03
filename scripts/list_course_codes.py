"""List Course codes (raw and trimmed) and flag potential collisions.

Usage examples (PowerShell):

  # Local (uses SQLite fallback if DATABASE_URL not set)
  python -m scripts.list_course_codes

  # JSON output (easier to share/copy)
  python -m scripts.list_course_codes --json

  # Inside Docker (Postgres), run in the web container to use DATABASE_URL
  docker compose exec web python -m scripts.list_course_codes

Notes:
- Running locally will not see production data unless DATABASE_URL is set.
- The app creates tables on startup; this script prints 0 rows if DB is empty.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any

from sqlmodel import select

from src.infrastructure.db.engine import session_scope
from src.infrastructure.db.models import Course


@dataclass
class Row:
    id: int
    name: str
    code_raw: str
    code_len: int
    trimmed: str
    trim_len: int


def gather_rows() -> tuple[list[Row], list[dict[str, Any]]]:
    rows: list[Row] = []
    with session_scope() as s:
        courses = s.exec(select(Course)).all()
        for c in courses:
            code = (c.code or "")
            trimmed = code.strip()
            rows.append(
                Row(
                    id=int(c.id or 0),
                    name=c.name,
                    code_raw=code,
                    code_len=len(code),
                    trimmed=trimmed,
                    trim_len=len(trimmed),
                )
            )
        # collisions after TRIM+lower
        buckets = defaultdict(list)
        for c in courses:
            norm = (c.code or "").strip().lower()
            if norm:
                buckets[norm].append(c)
        collisions = [
            {
                "key": k,
                "ids": [int(v.id or 0) for v in vs],
                "codes": [v.code for v in vs],
            }
            for k, vs in buckets.items()
            if len(vs) > 1
        ]
    return rows, collisions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print JSON output instead of a table")
    args = parser.parse_args()

    rows, collisions = gather_rows()
    if args.json:
        print(json.dumps({
            "total": len(rows),
            "rows": [asdict(r) for r in rows],
            "collisions": collisions,
        }, indent=2))
        return

    if not rows:
        print("Total courses: 0")
        return
    header = f"{'id':>4} | {'name':<30} | {'code(raw)':<20} | {'len':>3} | {'trimmed':<20} | {'trim_len':>8}"
    print(f"Total courses: {len(rows)}")
    print(header)
    print("-" * len(header))
    for r in rows:
        print(f"{r.id:4} | {r.name[:30]:<30} | {repr(r.code_raw):<20} | {r.code_len:3} | {repr(r.trimmed):<20} | {r.trim_len:8}")
    if collisions:
        print("\nPotential collisions after TRIM+lower():")
        for c in collisions:
            print(f"  {c['key']!r} -> ids {c['ids']} codes {c['codes']}")
    else:
        print("\nNo collisions after TRIM+lower().")


if __name__ == "__main__":
    main()
