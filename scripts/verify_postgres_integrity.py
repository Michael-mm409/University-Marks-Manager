"""
Quick health check for the Postgres migration.

Runs a set of validations:
- Presence of new columns (subjects.semester_id, *_subject_id)
- Null counts (should be 0 if backfill succeeded)
- Constraint existence (FKs and UNIQUEs added by the migration)
- NOT NULL status (where enforceable)
- Indexes created implicitly for UNIQUE constraints

Usage (inside the web container):

    python -m scripts.verify_postgres_integrity
"""
from __future__ import annotations

from typing import Iterable

from sqlalchemy import text
from sqlmodel import Session

from src.infrastructure.db.engine import engine


CONSTRAINTS = [
    ("subjects", "fk_subjects_semester_id"),
    ("subjects", "uq_subjects_semester_subject_code"),
    ("assignments", "fk_assignments_subject_id"),
    ("assignments", "uq_assignments_subject_assessment"),
    ("examinations", "fk_examinations_subject_id"),
    ("examinations", "uq_examinations_subject_id"),
    ("exam_settings", "fk_exam_settings_subject_id"),
    ("exam_settings", "uq_exam_settings_subject_id"),
]

NULL_CHECKS = [
    ("subjects", "semester_id"),
    ("assignments", "subject_id"),
    ("examinations", "subject_id"),
    ("exam_settings", "subject_id"),
]


def constraint_exists(session: Session, name: str) -> bool:
    sql = text(
        """
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_schema='public' AND constraint_name = :n
        """
    )
    return session.execute(sql, {"n": name}).first() is not None


essential_indexes = {
    # UNIQUE constraints will create backing indexes with auto-generated names; we
    # still list expected substrings so we can show the user what's present.
    "subjects": ["uq_subjects_semester_subject_code"],
    "assignments": ["uq_assignments_subject_assessment"],
    "examinations": ["uq_examinations_subject_id"],
    "exam_settings": ["uq_exam_settings_subject_id"],
}


def list_indexes(session: Session, table: str) -> list[str]:
    sql = text(
        """
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname='public' AND tablename = :t
        ORDER BY indexname
        """
    )
    rows = session.execute(sql, {"t": table}).all()
    return [r[0] for r in rows]


def count_nulls(session: Session, table: str, column: str) -> int:
    sql = text(f"SELECT COUNT(*) FROM public.{table} WHERE {column} IS NULL")
    row = session.execute(sql).first()
    return int(row[0]) if row else -1


def is_not_null(session: Session, table: str, column: str) -> bool:
    sql = text(
        """
        SELECT is_nullable
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name=:t AND column_name=:c
        """
    )
    row = session.execute(sql, {"t": table, "c": column}).first()
    if not row:
        return False
    return str(row[0]).upper() == "NO"


def orphan_counts(session: Session) -> dict[str, int]:
    results: dict[str, int] = {}
    # subjects -> semesters
    q_subj = text(
        """
        SELECT COUNT(*)
        FROM public.subjects s
        LEFT JOIN public.semesters sem ON sem.id = s.semester_id
        WHERE s.semester_id IS NOT NULL AND sem.id IS NULL
        """
    )
    row_subj = session.execute(q_subj).first()
    results["subjects.semester_id_orphans"] = int(row_subj[0]) if row_subj else 0

    # assignments -> subjects
    q_asn = text(
        """
        SELECT COUNT(*)
        FROM public.assignments a
        LEFT JOIN public.subjects s ON s.id = a.subject_id
        WHERE a.subject_id IS NOT NULL AND s.id IS NULL
        """
    )
    row_asn = session.execute(q_asn).first()
    results["assignments.subject_id_orphans"] = int(row_asn[0]) if row_asn else 0

    # examinations -> subjects
    q_exam = text(
        """
        SELECT COUNT(*)
        FROM public.examinations e
        LEFT JOIN public.subjects s ON s.id = e.subject_id
        WHERE e.subject_id IS NOT NULL AND s.id IS NULL
        """
    )
    row_exam = session.execute(q_exam).first()
    results["examinations.subject_id_orphans"] = int(row_exam[0]) if row_exam else 0

    # exam_settings -> subjects
    q_exs = text(
        """
        SELECT COUNT(*)
        FROM public.exam_settings es
        LEFT JOIN public.subjects s ON s.id = es.subject_id
        WHERE es.subject_id IS NOT NULL AND s.id IS NULL
        """
    )
    row_exs = session.execute(q_exs).first()
    results["exam_settings.subject_id_orphans"] = int(row_exs[0]) if row_exs else 0

    return results


def main() -> None:
    with Session(engine) as session:
        print("\n=== Constraint existence ===")
        for table, cname in CONSTRAINTS:
            print(f"{table}.{cname}: {constraint_exists(session, cname)}")

        print("\n=== Null counts after backfill (should be 0 ideally) ===")
        for table, col in NULL_CHECKS:
            print(f"{table}.{col} NULLs: {count_nulls(session, table, col)}")

        print("\n=== NOT NULL enforced? ===")
        for table, col in NULL_CHECKS:
            print(f"{table}.{col} NOT NULL: {is_not_null(session, table, col)}")

        print("\n=== Orphan checks (should be 0) ===")
        for k, v in orphan_counts(session).items():
            print(f"{k}: {v}")

        print("\n=== Indexes present ===")
        for table, expected in essential_indexes.items():
            idxs = list_indexes(session, table)
            print(f"{table}: {idxs}")

        print("\nDone.")


if __name__ == "__main__":
    main()
