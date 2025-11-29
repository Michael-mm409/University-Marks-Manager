"""
Migrate the database toward the UML target with surrogate IDs and FKs.

This script is designed for PostgreSQL and is idempotent. It performs:

1) Columns (add if missing)
   - subjects.semester_id INTEGER NULL
   - assignments.subject_id INTEGER NULL
   - examinations.subject_id INTEGER NULL
   - exam_settings.subject_id INTEGER NULL

2) Backfill values
   - subjects.semester_id from join (subjects.semester_name, subjects.year) -> semesters(id)
   - *_subject_id from join (subject_code, semester_name, year) -> subjects(id)

3) Constraints (add if missing)
   - subjects.semester_id NOT NULL (after backfill if all set)
   - FK subjects.semester_id -> semesters(id)
   - UNIQUE(subjects.semester_id, subjects.subject_code)
   - FK assignments.subject_id -> subjects(id)
   - UNIQUE(assignments.subject_id, assignments.assessment)
   - For examinations and exam_settings: add FK on subject_id and UNIQUE(subject_id).
     We keep existing composite PKs for now to avoid disruptive changes; a later step
     can replace PKs once the application is fully ID-based.

Usage (inside the web container):

    python -m scripts.migrate_to_surrogate_ids_postgres

Requires DATABASE_URL to point to Postgres.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlmodel import Session

from src.infrastructure.db.engine import engine


def column_exists(session: Session, table: str, column: str) -> bool:
    sql = text(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = :t AND column_name = :c
        """
    )
    res = session.execute(sql, {"t": table, "c": column})
    return res.first() is not None


def constraint_exists(session: Session, name: str) -> bool:
    sql = text(
        """
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_schema='public' AND constraint_name = :n
        """
    )
    res = session.execute(sql, {"n": name})
    return res.first() is not None


def index_exists(session: Session, name: str) -> bool:
    sql = text(
        """
        SELECT 1
        FROM pg_indexes
        WHERE schemaname='public' AND indexname = :n
        """
    )
    res = session.execute(sql, {"n": name})
    return res.first() is not None


def add_column_if_missing(session: Session, table: str, column: str, ddl: str) -> bool:
    if not column_exists(session, table, column):
        # ddl is the type/nullability portion (e.g., "INTEGER NULL"). Include the column name explicitly.
        session.execute(text(f"ALTER TABLE public.{table} ADD COLUMN {column} {ddl}"))
        return True
    return False


def add_unique_if_missing(session: Session, table: str, name: str, columns: str) -> bool:
    if not constraint_exists(session, name):
        session.execute(text(f"ALTER TABLE public.{table} ADD CONSTRAINT {name} UNIQUE ({columns})"))
        return True
    return False


def add_fk_if_missing(session: Session, table: str, name: str, column: str, ref: str, on_delete: Optional[str] = None) -> bool:
    if not constraint_exists(session, name):
        od = f" ON DELETE {on_delete}" if on_delete else ""
        session.execute(text(f"ALTER TABLE public.{table} ADD CONSTRAINT {name} FOREIGN KEY ({column}) REFERENCES public.{ref}{od}"))
        return True
    return False


def set_not_null_if_possible(session: Session, table: str, column: str) -> bool:
    # Only set NOT NULL when no NULLs remain
    res = session.execute(text(f"SELECT COUNT(*) FROM public.{table} WHERE {column} IS NULL"))
    row = res.first()
    nulls = int(row[0]) if row is not None else 0
    if nulls == 0:
        session.execute(text(f"ALTER TABLE public.{table} ALTER COLUMN {column} SET NOT NULL"))
        return True
    return False


def backfill_subjects_semester_id(session: Session) -> int:
    # Join by (semester_name, year) -> semesters(id)
    sql = text(
        """
        UPDATE public.subjects s
        SET semester_id = sem.id
        FROM public.semesters sem
        WHERE s.semester_id IS NULL
          AND sem.name = s.semester_name
          AND sem.year::text = s.year::text
        """
    )
    res = session.execute(sql)
    # rowcount available via .rowcount on result proxy in SQLAlchemy 1.4; use cursor attribute
    try:
        return res.rowcount  # type: ignore[attr-defined]
    except Exception:
        return 0


def backfill_child_subject_ids(session: Session, table: str) -> int:
    # Update table.subject_id from subjects natural key mapping
    sql = text(
        f"""
        UPDATE public.{table} c
        SET subject_id = s.id
        FROM public.subjects s
        WHERE c.subject_id IS NULL
          AND s.subject_code = c.subject_code
          AND s.semester_name = c.semester_name
          AND s.year = c.year
        """
    )
    res = session.execute(sql)
    try:
        return res.rowcount  # type: ignore[attr-defined]
    except Exception:
        return 0


def run() -> None:
    with Session(engine) as session:
        # 1) Add columns
        added = []
        if add_column_if_missing(session, "subjects", "semester_id", "INTEGER NULL"):
            added.append("subjects.semester_id")
        if add_column_if_missing(session, "assignments", "subject_id", "INTEGER NULL"):
            added.append("assignments.subject_id")
        if add_column_if_missing(session, "examinations", "subject_id", "INTEGER NULL"):
            added.append("examinations.subject_id")
        if add_column_if_missing(session, "exam_settings", "subject_id", "INTEGER NULL"):
            added.append("exam_settings.subject_id")
        if added:
            session.commit()
            print("Added columns:", ", ".join(added))

        # 2) Backfill values
        n_subj = backfill_subjects_semester_id(session)
        n_assign = backfill_child_subject_ids(session, "assignments")
        n_exam = backfill_child_subject_ids(session, "examinations")
        n_exset = backfill_child_subject_ids(session, "exam_settings")
        session.commit()
        print(f"Backfilled: subjects.semester_id={n_subj}, assignments.subject_id={n_assign}, examinations.subject_id={n_exam}, exam_settings.subject_id={n_exset}")

        # 3) Constraints
        # 3a) FKs
        if add_fk_if_missing(session, "subjects", "fk_subjects_semester_id", "semester_id", "semesters(id)"):
            print("Added FK subjects.semester_id -> semesters(id)")
        if add_fk_if_missing(session, "assignments", "fk_assignments_subject_id", "subject_id", "subjects(id)", on_delete="CASCADE"):
            print("Added FK assignments.subject_id -> subjects(id) ON DELETE CASCADE")
        if add_fk_if_missing(session, "examinations", "fk_examinations_subject_id", "subject_id", "subjects(id)", on_delete="CASCADE"):
            print("Added FK examinations.subject_id -> subjects(id) ON DELETE CASCADE")
        if add_fk_if_missing(session, "exam_settings", "fk_exam_settings_subject_id", "subject_id", "subjects(id)", on_delete="CASCADE"):
            print("Added FK exam_settings.subject_id -> subjects(id) ON DELETE CASCADE")
        session.commit()

        # 3b) Uniques
        if add_unique_if_missing(session, "subjects", "uq_subjects_semester_subject_code", "semester_id, subject_code"):
            print("Added UNIQUE(subjects.semester_id, subjects.subject_code)")
        if add_unique_if_missing(session, "assignments", "uq_assignments_subject_assessment", "subject_id, assessment"):
            print("Added UNIQUE(assignments.subject_id, assignments.assessment)")
        if add_unique_if_missing(session, "examinations", "uq_examinations_subject_id", "subject_id"):
            print("Added UNIQUE(examinations.subject_id)")
        if add_unique_if_missing(session, "exam_settings", "uq_exam_settings_subject_id", "subject_id"):
            print("Added UNIQUE(exam_settings.subject_id)")
        session.commit()

        # 3c) Tighten NOT NULL where possible (safe only if no NULLs remain)
        if set_not_null_if_possible(session, "subjects", "semester_id"):
            print("Set subjects.semester_id NOT NULL")
        if set_not_null_if_possible(session, "assignments", "subject_id"):
            print("Set assignments.subject_id NOT NULL")
        if set_not_null_if_possible(session, "examinations", "subject_id"):
            print("Set examinations.subject_id NOT NULL")
        if set_not_null_if_possible(session, "exam_settings", "subject_id"):
            print("Set exam_settings.subject_id NOT NULL")
        session.commit()

        print("Migration to surrogate IDs completed (phase 1). You may refactor app code to use IDs internally.\n"
              "Later, you can drop legacy composite columns and replace composite PKs with subject_id as PK for exams/settings.")


if __name__ == "__main__":
    run()
