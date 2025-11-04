"""
One-off migration: copy data from an existing SQLite database into Postgres.

Usage (inside the web container so DATABASE_URL is set):

    python -m scripts.migrate_sqlite_to_postgres --sqlite /app/data/old_marks.db

The script is idempotent: it checks for existing rows before inserting.
It migrates semesters, subjects, assignments, examinations, and exam_settings.

Courses are not migrated (they didn't exist previously). After migration,
use the Course pages to assign semesters and auto-link subjects as needed.
"""
from __future__ import annotations

import argparse
from typing import Iterable, Tuple

from sqlalchemy import create_engine as sa_create_engine, text
from sqlalchemy.engine import Engine, Row
from sqlmodel import Session, select

from src.infrastructure.db.engine import engine as pg_engine
from src.infrastructure.db.models import (
    Semester,
    Subject,
    Assignment,
    Examination,
    ExamSettings,
)


def table_exists(sqlite_engine: Engine, table_name: str) -> bool:
    """Case-insensitive table existence check for SQLite."""
    with sqlite_engine.connect() as conn:
        res = conn.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type='table' AND lower(name)=lower(:t)"
            ),
            {"t": table_name},
        ).fetchone()
        return res is not None


def resolve_table_name(sqlite_engine: Engine, *candidates: str) -> str | None:
    """Return the actual table name in SQLite matching any of the candidates (case-insensitive)."""
    lowered = [c.lower() for c in candidates]
    with sqlite_engine.connect() as conn:
        rows = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        for (name,) in rows:
            if name.lower() in lowered:
                return name
    return None


def fetch_all(sqlite_engine: Engine, sql: str) -> list[Row]:
    with sqlite_engine.connect() as conn:
        return list(conn.execute(text(sql)))


def upsert_semesters(pg_sess: Session, semesters: Iterable[Tuple[str, str | int]]):
    created = 0
    for name, year in semesters:
        try:
            y = int(year)
        except Exception:
            # Fallback for non-numeric year values
            try:
                y = int(str(year).strip())
            except Exception:
                continue
        exists = pg_sess.exec(
            select(Semester).where(Semester.name == name, Semester.year == y)
        ).first()
        if not exists:
            pg_sess.add(Semester(name=name, year=y))
            created += 1
    if created:
        pg_sess.commit()
    return created


def upsert_subjects(pg_sess: Session, rows: list[Row]):
    created = 0
    for r in rows:
        # Compatible with typical legacy columns
        subject_code = r._mapping.get("subject_code") or r._mapping.get("code")
        semester_name = r._mapping.get("semester_name") or r._mapping.get("semester")
        year = r._mapping.get("year")
        subject_name = r._mapping.get("subject_name") or r._mapping.get("name")
        total_mark = r._mapping.get("total_mark")
        sync_subject = r._mapping.get("sync_subject")

        if subject_code is None or semester_name is None or year is None or subject_name is None:
            continue

        # Check if already present by natural key (code+semester+year)
        exists = pg_sess.exec(
            select(Subject).where(
                Subject.subject_code == str(subject_code),
                Subject.semester_name == str(semester_name),
                Subject.year == str(year),
            )
        ).first()
        if exists:
            continue

        pg_sess.add(
            Subject(
                subject_code=str(subject_code),
                semester_name=str(semester_name),
                year=str(year),
                subject_name=str(subject_name),
                total_mark=float(total_mark) if total_mark not in (None, "") else 0.0,
                sync_subject=bool(sync_subject) if sync_subject is not None else False,
            )
        )
        created += 1
    if created:
        pg_sess.commit()
    return created


def upsert_assignments(pg_sess: Session, rows: list[Row]):
    created = 0
    for r in rows:
        assessment = str(r._mapping.get("assessment"))
        subject_code = str(r._mapping.get("subject_code"))
        semester_name = str(r._mapping.get("semester_name"))
        year = str(r._mapping.get("year"))
        grade_type = str(r._mapping.get("grade_type", "numeric"))

        # Skip if this record already exists in Postgres
        exists = pg_sess.exec(
            select(Assignment).where(
                Assignment.assessment == assessment,
                Assignment.subject_code == subject_code,
                Assignment.semester_name == semester_name,
                Assignment.year == year,
            )
        ).first()
        if exists:
            continue

        # Initialize marks to None
        w_mark, uw_mark, m_weight = None, None, None

        # ONLY attempt to convert to float if the grade is numeric
        if grade_type.lower() == "numeric":
            raw_w_mark = r._mapping.get("weighted_mark")
            raw_uw_mark = r._mapping.get("unweighted_mark")
            raw_m_weight = r._mapping.get("mark_weight")

            # Safely convert each value, checking for valid content first
            if raw_w_mark is not None and str(raw_w_mark).strip() != "":
                try:
                    w_mark = float(raw_w_mark)
                except (ValueError, TypeError):
                    pass  # Keep as None if conversion fails
            
            if raw_uw_mark is not None and str(raw_uw_mark).strip() != "":
                try:
                    uw_mark = float(raw_uw_mark)
                except (ValueError, TypeError):
                    pass

            if raw_m_weight is not None and str(raw_m_weight).strip() != "":
                try:
                    m_weight = float(raw_m_weight)
                except (ValueError, TypeError):
                    pass

        pg_sess.add(
            Assignment(
                assessment=assessment,
                subject_code=subject_code,
                semester_name=semester_name,
                year=year,
                weighted_mark=w_mark,
                unweighted_mark=uw_mark,
                mark_weight=m_weight,
                grade_type=grade_type,
            )
        )
        created += 1
    if created:
        pg_sess.commit()
    return created


def upsert_exams(pg_sess: Session, rows: list[Row]):
    created = 0
    for r in rows:
        subject_code = str(r._mapping.get("subject_code"))
        semester_name = str(r._mapping.get("semester_name"))
        year = str(r._mapping.get("year"))
        exam_mark = r._mapping.get("exam_mark")
        exam_weight = r._mapping.get("exam_weight")

        if not (subject_code and semester_name and year):
            continue

        exists = pg_sess.get(Examination, (subject_code, semester_name, year))
        if exists:
            continue

        pg_sess.add(
            Examination(
                subject_code=subject_code,
                semester_name=semester_name,
                year=year,
                exam_mark=float(exam_mark) if exam_mark not in (None, "") else 0.0,
                exam_weight=float(exam_weight) if exam_weight not in (None, "") else 100.0,
            )
        )
        created += 1
    if created:
        pg_sess.commit()
    return created


def upsert_exam_settings(pg_sess: Session, rows: list[Row]):
    created = 0
    for r in rows:
        subject_code = str(r._mapping.get("subject_code"))
        semester_name = str(r._mapping.get("semester_name"))
        year = str(r._mapping.get("year"))
        ps_exam = r._mapping.get("ps_exam")
        ps_factor = r._mapping.get("ps_factor")

        if not (subject_code and semester_name and year):
            continue

        exists = pg_sess.get(ExamSettings, (subject_code, semester_name, year))
        if exists:
            continue

        pg_sess.add(
            ExamSettings(
                subject_code=subject_code,
                semester_name=semester_name,
                year=year,
                ps_exam=bool(ps_exam) if ps_exam is not None else False,
                ps_factor=float(ps_factor) if ps_factor not in (None, "") else 40.0,
            )
        )
        created += 1
    if created:
        pg_sess.commit()
    return created


def main():
    parser = argparse.ArgumentParser(description="Migrate data from SQLite to Postgres or inspect the SQLite file")
    parser.add_argument("--sqlite", required=True, help="Path to the legacy SQLite .db file (inside the container)")
    parser.add_argument("--inspect", action="store_true", help="Only inspect the SQLite DB: list tables, counts, schema, and a few sample rows")
    parser.add_argument("--limit", type=int, default=5, help="Rows to show per table when --inspect is used (default: 5)")
    args = parser.parse_args()

    sqlite_url = f"sqlite:///{args.sqlite}"
    sqlite_engine = sa_create_engine(sqlite_url)

    # Inspect mode: print out tables, counts, schema, and some sample rows
    if args.inspect:
        with sqlite_engine.connect() as conn:
            print(f"Inspecting SQLite DB at: {args.sqlite}")
            tables = [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))]
            if not tables:
                print("No tables found in the SQLite file.")
                return
            for t in tables:
                print(f"\n=== Table: {t} ===")
                # Count
                try:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
                    print(f"count: {count}")
                except Exception as e:
                    print(f"count: <error> {e}")
                # Schema
                try:
                    schema_rows = conn.execute(text(f"PRAGMA table_info('{t}')")).fetchall()
                    print("columns:")
                    for sr in schema_rows:
                        # PRAGMA table_info: cid, name, type, notnull, dflt_value, pk
                        print(f"  - {sr[1]} ({sr[2]}){' PRIMARY KEY' if sr[5] else ''}")
                except Exception as e:
                    print(f"schema: <error> {e}")
                # Sample
                try:
                    sample = conn.execute(text(f"SELECT * FROM {t} LIMIT {args.limit}")).fetchall()
                    print("sample:")
                    for row in sample:
                        print(dict(row._mapping))
                except Exception as e:
                    print(f"sample: <error> {e}")
        return

    # Migration mode
    # Quick table presence checks
    # Resolve actual table names case-insensitively (SQLite stores as created)
    semesters_tbl = resolve_table_name(sqlite_engine, "semesters")
    subjects_tbl = resolve_table_name(sqlite_engine, "subjects")
    assignments_tbl = resolve_table_name(sqlite_engine, "assignments")
    examinations_tbl = resolve_table_name(sqlite_engine, "examinations", "exams")
    exam_settings_tbl = resolve_table_name(sqlite_engine, "exam_settings")

    with Session(pg_engine) as pg_sess:
        # Migrate semesters
        semesters: list[tuple[str, str | int]] = []
        if semesters_tbl:
            for row in fetch_all(sqlite_engine, f"SELECT name, year FROM {semesters_tbl}"):
                semesters.append((row[0], row[1]))
        elif subjects_tbl:
            # Derive from subjects when semesters table didn't exist in legacy DB
            for row in fetch_all(sqlite_engine, f"SELECT DISTINCT semester_name, year FROM {subjects_tbl}"):
                semesters.append((row[0], row[1]))

        created_sem = upsert_semesters(pg_sess, semesters)

        # Migrate subjects
        if subjects_tbl:
            subj_rows = fetch_all(sqlite_engine, f"SELECT * FROM {subjects_tbl}")
            created_subj = upsert_subjects(pg_sess, subj_rows)
        else:
            created_subj = 0

        # Migrate assignments
        if assignments_tbl:
            created_assess = upsert_assignments(pg_sess, fetch_all(sqlite_engine, f"SELECT * FROM {assignments_tbl}"))
        else:
            created_assess = 0

        # Migrate examinations
        if examinations_tbl:
            created_exams = upsert_exams(pg_sess, fetch_all(sqlite_engine, f"SELECT * FROM {examinations_tbl}"))
        else:
            created_exams = 0

        # Migrate exam settings
        if exam_settings_tbl:
            created_settings = upsert_exam_settings(pg_sess, fetch_all(sqlite_engine, f"SELECT * FROM {exam_settings_tbl}"))
        else:
            created_settings = 0

    print(
        "Migration complete. Created -> Semesters: %s, Subjects: %s, Assignments: %s, Examinations: %s, ExamSettings: %s"
        % (created_sem, created_subj, created_assess, created_exams, created_settings)
    )


if __name__ == "__main__":
    main()
