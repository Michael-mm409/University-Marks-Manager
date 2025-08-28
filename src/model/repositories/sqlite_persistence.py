"""SQLite-backed data persistence layer.

This module introduces an alternative to the JSON `DataPersistence` class
without breaking existing code. It mirrors the public interface (`load_data`,
`save_data`, and `.data` attribute) so it can be swapped in gradually.

Design goals:
    - Preserve existing in‑memory structure: Dict[semester_name, Dict[code, Subject]]
    - Support S/U grade types (store `weighted_mark` as TEXT, parse back)
    - Keep schema minimal & explicit, easy to evolve
    - Allow idempotent writes (simple upsert semantics)

Schema (normalized light):
    subjects(
        id INTEGER PRIMARY KEY,
        subject_code TEXT,
        subject_name TEXT,
        semester_name TEXT,
        year TEXT,
        total_mark REAL,
        sync_subject INTEGER
    )

    assignments(
        id INTEGER PRIMARY KEY,
        subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
        assessment TEXT,
        weighted_mark TEXT,          -- stored as text to allow "S" / "U" / numeric
        unweighted_mark REAL,
        mark_weight REAL,
        grade_type TEXT
    )

    examinations(
        id INTEGER PRIMARY KEY,
        subject_id INTEGER UNIQUE REFERENCES subjects(id) ON DELETE CASCADE,
        exam_mark REAL,
        exam_weight REAL
    )

Migration strategy:
    1. Instantiate legacy JSON DataPersistence(year) and read `.data`.
    2. Instantiate DataPersistenceSQLite(db_path="data/marks.db").
    3. Call `save_data(json_persistence.data)` once.
    4. Switch controller factory to use DataPersistenceSQLite.

Switching:
    In `controller/app_controller.py` pass `data_persistence_factory=DataPersistenceSQLite`.

Limitations / Future:
    - Currently `save_data` overwrites (per subject) via delete+insert. Fine for scale here.
    - No fine‑grained dirty tracking yet.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Protocol, Tuple, runtime_checkable

from model.domain.entities import Assignment, Examination, Subject
from model.enums import GradeType


@dataclass(slots=True)
class _SubjectRow:
    id: int
    subject_code: str
    subject_name: str
    semester_name: str
    year: str
    total_mark: float
    sync_subject: bool


@runtime_checkable
class PersistenceProtocol(Protocol):  # minimal protocol for duck typing
    year: str
    data: Dict[str, Dict[str, Subject]]

    def load_data(self) -> Dict[str, Dict[str, Subject]]: ...  # noqa: E701
    def save_data(self, semesters: Dict[str, Dict[str, Subject]]) -> None: ...  # noqa: E701


class DataPersistenceSQLite:
    """SQLite implementation mirroring JSON persistence public surface.

    Parameters:
        year: Academic year to load / manage.
        db_path: Path to sqlite database file.
        semesters_if_new: Optional list of semester names to create automatically
            if this `year` has no semesters yet. If None and the year is new,
            an interactive prompt (stdin) will ask for a comma‑separated list.
            (Prompt is skipped when stdin is not a TTY.)
    """

    def __init__(self, year: str, db_path: str = "data/marks.db", semesters_if_new: List[str] | None = None):
        self.year = year
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._ensure_schema()
        self._maybe_initialize_year(semesters_if_new)
        self.data: Dict[str, Dict[str, Subject]] = self.load_data()

    def _maybe_initialize_year(self, semesters_if_new: List[str] | None) -> None:
        """If no semesters exist for this year, create them (optionally prompting user)."""
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM semesters WHERE year=?", (self.year,))
        count = cur.fetchone()[0]
        if count > 0:
            return
        # Determine list
        semesters: List[str]
        if semesters_if_new is not None and len(semesters_if_new) > 0:
            semesters = semesters_if_new
        else:
            # Default silently to a single generic semester; UI will offer initialization
            semesters = ["Semester 1"]

        cur.executemany(
            "INSERT OR IGNORE INTO semesters(name, year) VALUES(?,?)",
            [(s, self.year) for s in semesters],
        )
        self._conn.commit()

    # --- schema ---
    def _ensure_schema(self) -> None:
        """Ensure schema (and migrations) are applied.

        v1 schema used numeric subject_id FK in assignments / examinations.
        v2 schema stores (subject_code, semester_name, year) directly with a composite FK to subjects.
        """
        cur = self._conn.cursor()
        cur.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS semesters (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                year TEXT NOT NULL,
                UNIQUE(name, year)
            );
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                subject_code TEXT NOT NULL,
                subject_name TEXT NOT NULL,
                semester_name TEXT NOT NULL,
                year TEXT NOT NULL,
                total_mark REAL NOT NULL DEFAULT 0,
                sync_subject INTEGER NOT NULL DEFAULT 0,
                UNIQUE(subject_code, semester_name, year),
                FOREIGN KEY(semester_name, year) REFERENCES semesters(name, year) ON DELETE CASCADE
            );
            /* v2 target tables */
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY,
                subject_code TEXT NOT NULL,
                semester_name TEXT NOT NULL,
                year TEXT NOT NULL,
                assessment TEXT NOT NULL,
                weighted_mark TEXT,
                unweighted_mark REAL,
                mark_weight REAL,
                grade_type TEXT NOT NULL,
                UNIQUE(subject_code, semester_name, year, assessment)
            );
            CREATE TABLE IF NOT EXISTS examinations (
                id INTEGER PRIMARY KEY,
                subject_code TEXT NOT NULL,
                semester_name TEXT NOT NULL,
                year TEXT NOT NULL,
                exam_mark REAL NOT NULL DEFAULT 0,
                exam_weight REAL NOT NULL DEFAULT 100,
                UNIQUE(subject_code, semester_name, year)
            );
            """
        )
        self._conn.commit()
        # Detect legacy subject_id based assignments (pre‑migration) and migrate if needed
        cur.execute("PRAGMA table_info(assignments)")
        cols = {r[1] for r in cur.fetchall()}
        if "subject_id" in cols and "subject_code" not in cols:
            self._migrate_v1_to_v2()
        # Ensure subjects table has FK to semesters; if not, migrate
        if not self._subjects_has_sem_fk():
            self._migrate_add_semester_fk()
        # Ensure assignments/examinations carry composite FK to subjects; if not, migrate
        if not self._assignments_has_subject_fk():
            self._migrate_add_subject_fk_to_child_tables()

    def _migrate_v1_to_v2(self) -> None:
        """Migrate legacy v1 tables (assignments/examinations using subject_id) to v2 natural key form.

        Safe to run multiple times (idempotent guard by checking for subject_id column before invocation).
        """
        cur = self._conn.cursor()
        cur.execute("PRAGMA foreign_keys=OFF;")
        # Create new tables with natural keys
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS assignments_v2 (
                id INTEGER PRIMARY KEY,
                subject_code TEXT NOT NULL,
                semester_name TEXT NOT NULL,
                year TEXT NOT NULL,
                assessment TEXT NOT NULL,
                weighted_mark TEXT,
                unweighted_mark REAL,
                mark_weight REAL,
                grade_type TEXT NOT NULL,
                UNIQUE(subject_code, semester_name, year, assessment)
            );
            CREATE TABLE IF NOT EXISTS examinations_v2 (
                id INTEGER PRIMARY KEY,
                subject_code TEXT NOT NULL,
                semester_name TEXT NOT NULL,
                year TEXT NOT NULL,
                exam_mark REAL NOT NULL DEFAULT 0,
                exam_weight REAL NOT NULL DEFAULT 100,
                UNIQUE(subject_code, semester_name, year)
            );
            """
        )
        # Copy assignments
        cur.execute(
            """
            INSERT OR IGNORE INTO assignments_v2(id, subject_code, semester_name, year, assessment, weighted_mark, unweighted_mark, mark_weight, grade_type)
            SELECT a.id, s.subject_code, s.semester_name, s.year, a.assessment, a.weighted_mark, a.unweighted_mark, a.mark_weight, a.grade_type
            FROM assignments a JOIN subjects s ON a.subject_id = s.id;
            """
        )
        # Copy exams if legacy structure present
        cur.execute("PRAGMA table_info(examinations)")
        ecols = {r[1] for r in cur.fetchall()}
        if "subject_id" in ecols and "subject_code" not in ecols:
            cur.execute(
                """
                INSERT OR IGNORE INTO examinations_v2(id, subject_code, semester_name, year, exam_mark, exam_weight)
                SELECT e.id, s.subject_code, s.semester_name, s.year, e.exam_mark, e.exam_weight
                FROM examinations e JOIN subjects s ON e.subject_id = s.id;
                """
            )
        cur.execute("PRAGMA foreign_keys=ON;")
        self._conn.commit()

    # ---- FK Migrations ----
    def _subjects_has_sem_fk(self) -> bool:
        cur = self._conn.cursor()
        cur.execute("PRAGMA foreign_key_list(subjects)")
        for row in cur.fetchall():
            if row[2] == "semesters":  # references table
                return True
        return False

    def _assignments_has_subject_fk(self) -> bool:
        cur = self._conn.cursor()
        cur.execute("PRAGMA foreign_key_list(assignments)")
        for row in cur.fetchall():
            if row[2] == "subjects":
                return True
        return False

    def _migrate_add_semester_fk(self) -> None:
        cur = self._conn.cursor()
        cur.execute("PRAGMA foreign_keys=OFF;")
        # Ensure corresponding semesters exist
        cur.execute("SELECT DISTINCT semester_name, year FROM subjects")
        for sem_name, year in cur.fetchall():
            cur.execute("INSERT OR IGNORE INTO semesters(name, year) VALUES(?,?)", (sem_name, year))
        # Rebuild subjects with FK constraint
        cur.executescript(
            """
            CREATE TABLE subjects_new (
                id INTEGER PRIMARY KEY,
                subject_code TEXT NOT NULL,
                subject_name TEXT NOT NULL,
                semester_name TEXT NOT NULL,
                year TEXT NOT NULL,
                total_mark REAL NOT NULL DEFAULT 0,
                sync_subject INTEGER NOT NULL DEFAULT 0,
                UNIQUE(subject_code, semester_name, year),
                FOREIGN KEY(semester_name, year) REFERENCES semesters(name, year) ON DELETE CASCADE
            );
            INSERT INTO subjects_new(id, subject_code, subject_name, semester_name, year, total_mark, sync_subject)
            SELECT id, subject_code, subject_name, semester_name, year, total_mark, sync_subject FROM subjects;
            DROP TABLE subjects;
            ALTER TABLE subjects_new RENAME TO subjects;
            """
        )
        cur.execute("PRAGMA foreign_keys=ON;")
        self._conn.commit()

    def _migrate_add_subject_fk_to_child_tables(self) -> None:
        cur = self._conn.cursor()
        cur.execute("PRAGMA foreign_keys=OFF;")
        # Assignments
        cur.executescript(
            """
            CREATE TABLE assignments_new (
                id INTEGER PRIMARY KEY,
                subject_code TEXT NOT NULL,
                semester_name TEXT NOT NULL,
                year TEXT NOT NULL,
                assessment TEXT NOT NULL,
                weighted_mark TEXT,
                unweighted_mark REAL,
                mark_weight REAL,
                grade_type TEXT NOT NULL,
                UNIQUE(subject_code, semester_name, year, assessment),
                FOREIGN KEY(subject_code, semester_name, year) REFERENCES subjects(subject_code, semester_name, year) ON DELETE CASCADE
            );
            INSERT OR IGNORE INTO assignments_new(id, subject_code, semester_name, year, assessment, weighted_mark, unweighted_mark, mark_weight, grade_type)
            SELECT id, subject_code, semester_name, year, assessment, weighted_mark, unweighted_mark, mark_weight, grade_type FROM assignments;
            DROP TABLE assignments;
            ALTER TABLE assignments_new RENAME TO assignments;
            CREATE TABLE examinations_new (
                id INTEGER PRIMARY KEY,
                subject_code TEXT NOT NULL,
                semester_name TEXT NOT NULL,
                year TEXT NOT NULL,
                exam_mark REAL NOT NULL DEFAULT 0,
                exam_weight REAL NOT NULL DEFAULT 100,
                UNIQUE(subject_code, semester_name, year),
                FOREIGN KEY(subject_code, semester_name, year) REFERENCES subjects(subject_code, semester_name, year) ON DELETE CASCADE
            );
            INSERT OR IGNORE INTO examinations_new(id, subject_code, semester_name, year, exam_mark, exam_weight)
            SELECT id, subject_code, semester_name, year, exam_mark, exam_weight FROM examinations;
            DROP TABLE examinations;
            ALTER TABLE examinations_new RENAME TO examinations;
            """
        )
        cur.execute("PRAGMA foreign_keys=ON;")
        self._conn.commit()

    # --- load ---
    def load_data(self) -> Dict[str, Dict[str, Subject]]:
        """Load all semester data for the configured year into nested dict structure."""
        database_cursor = self._conn.cursor()
        database_cursor.execute(
            """
            SELECT * FROM subjects WHERE year = ?
            """,
            (self.year,),
        )
        subjects_rows = [_SubjectRow(**dict(subject_record)) for subject_record in database_cursor.fetchall()]

        # Determine schema variant (v2 has subject_code column in assignments)
        database_cursor.execute("PRAGMA table_info(assignments)")
        assignment_cols = {r[1] for r in database_cursor.fetchall()}
        v2 = "subject_code" in assignment_cols

        if v2:
            assignments_map_v2: Dict[Tuple[str, str], List[Assignment]] = {}
            exams_map_v2: Dict[Tuple[str, str], Examination] = {}
            database_cursor.execute("SELECT * FROM assignments WHERE year=?", (self.year,))
            for row in database_cursor.fetchall():
                grade_raw = row["grade_type"] or GradeType.NUMERIC.value
                try:
                    grade_type = GradeType(grade_raw)
                except ValueError:
                    grade_type = GradeType.NUMERIC
                wm_txt = row["weighted_mark"]
                if wm_txt in (GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value):
                    w_mark = wm_txt
                else:
                    try:
                        w_mark = float(wm_txt) if wm_txt is not None else 0.0
                    except ValueError:
                        w_mark = 0.0
                assignments_map_v2.setdefault((row["semester_name"], row["subject_code"]), []).append(
                    Assignment(
                        subject_assessment=row["assessment"],
                        weighted_mark=w_mark,
                        unweighted_mark=row["unweighted_mark"],
                        mark_weight=row["mark_weight"],
                        grade_type=grade_type,
                    )
                )
            database_cursor.execute("SELECT * FROM examinations WHERE year=?", (self.year,))
            exams_map_v2 = {
                (row["semester_name"], row["subject_code"]): Examination(
                    exam_mark=row["exam_mark"], exam_weight=row["exam_weight"]
                )
                for row in database_cursor.fetchall()
            }
        else:
            # Legacy (v1) path with numeric subject_id mapping
            subj_ids = [sr.id for sr in subjects_rows]
            assignments_map_v1: Dict[int, List[Assignment]] = {}
            exams_map_v1: Dict[int, Examination] = {}
            if subj_ids:
                qmarks = ",".join(["?"] * len(subj_ids))
                database_cursor.execute(f"SELECT * FROM assignments WHERE subject_id IN ({qmarks})", subj_ids)
                for row in database_cursor.fetchall():
                    grade_raw = row["grade_type"] or GradeType.NUMERIC.value
                    try:
                        grade_type = GradeType(grade_raw)
                    except ValueError:
                        grade_type = GradeType.NUMERIC
                    wm_txt = row["weighted_mark"]
                    if wm_txt in (GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value):
                        w_mark = wm_txt
                    else:
                        try:
                            w_mark = float(wm_txt) if wm_txt is not None else 0.0
                        except ValueError:
                            w_mark = 0.0
                    assignments_map_v1.setdefault(row["subject_id"], []).append(
                        Assignment(
                            subject_assessment=row["assessment"],
                            weighted_mark=w_mark,
                            unweighted_mark=row["unweighted_mark"],
                            mark_weight=row["mark_weight"],
                            grade_type=grade_type,
                        )
                    )
                database_cursor.execute(f"SELECT * FROM examinations WHERE subject_id IN ({qmarks})", subj_ids)
                for row in database_cursor.fetchall():
                    exams_map_v1[row["subject_id"]] = Examination(
                        exam_mark=row["exam_mark"], exam_weight=row["exam_weight"]
                    )

        data: Dict[str, Dict[str, Subject]] = {}
        for sr in subjects_rows:
            sem_key = sr.semester_name
            data.setdefault(sem_key, {})
            if v2:
                assignments_list = assignments_map_v2.get((sr.semester_name, sr.subject_code), [])
                exam_obj = exams_map_v2.get((sr.semester_name, sr.subject_code), Examination())
            else:  # legacy path
                assignments_list = assignments_map_v1.get(sr.id, [])
                exam_obj = exams_map_v1.get(sr.id, Examination())
            data[sem_key][sr.subject_code] = Subject(
                subject_code=sr.subject_code,
                subject_name=sr.subject_name,
                assignments=assignments_list,
                total_mark=sr.total_mark,
                examinations=exam_obj,
                sync_subject=sr.sync_subject,
            )
        return data

    # --- save ---
    def save_data(self, semesters: Dict[str, Dict[str, Subject]]) -> None:
        """Persist nested semester structure for this year.

        Strategy: for the current *year* we upsert subjects; for each subject we
        delete existing assignments/exam then re-insert (simplifies logic given
        modest data volume).
        """
        cur = self._conn.cursor()

        for semester_name, subjects in semesters.items():
            if not isinstance(subjects, dict):  # skip malformed
                continue
            for code, subject in subjects.items():
                # Upsert subject
                cur.execute(
                    """
                    INSERT INTO subjects(subject_code, subject_name, semester_name, year, total_mark, sync_subject)
                    VALUES(?,?,?,?,?,?)
                    ON CONFLICT(subject_code, semester_name, year) DO UPDATE SET
                        subject_name=excluded.subject_name,
                        total_mark=excluded.total_mark,
                        sync_subject=excluded.sync_subject
                    """,
                    (
                        code,
                        subject.subject_name,
                        semester_name,
                        self.year,
                        subject.total_mark,
                        1 if subject.sync_subject else 0,
                    ),
                )
                # Replace assignments using natural key (safe for both schemas; DELETE ignores unknown columns)
                cur.execute(
                    "DELETE FROM assignments WHERE subject_code=? AND semester_name=? AND year=?",
                    (code, semester_name, self.year),
                )
                for a in subject.assignments:
                    cur.execute(
                        """
                        INSERT OR REPLACE INTO assignments(subject_code, semester_name, year, assessment, weighted_mark, unweighted_mark, mark_weight, grade_type)
                        VALUES(?,?,?,?,?,?,?,?)
                        """,
                        (
                            code,
                            semester_name,
                            self.year,
                            a.subject_assessment,
                            str(a.weighted_mark) if a.weighted_mark is not None else None,
                            a.unweighted_mark,
                            a.mark_weight,
                            a.grade_type.value,
                        ),
                    )
                # Replace examination
                cur.execute(
                    "DELETE FROM examinations WHERE subject_code=? AND semester_name=? AND year=?",
                    (code, semester_name, self.year),
                )
                if subject.examinations:
                    cur.execute(
                        "INSERT INTO examinations(subject_code, semester_name, year, exam_mark, exam_weight) VALUES(?,?,?,?,?)",
                        (
                            code,
                            semester_name,
                            self.year,
                            subject.examinations.exam_mark,
                            subject.examinations.exam_weight,
                        ),
                    )

        self._conn.commit()
        # Refresh in-memory snapshot
        self.data = self.load_data()

    # --------- Semester operations ---------
    def list_semesters(self) -> List[str]:
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT name FROM semesters WHERE year=?
            UNION
            SELECT DISTINCT semester_name AS name FROM subjects WHERE year=?
            ORDER BY name COLLATE NOCASE
            """,
            (self.year, self.year),
        )
        return [r[0] for r in cur.fetchall()]

    def add_semester(self, name: str) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO semesters(name, year) VALUES(?,?)",
            (name, self.year),
        )
        self._conn.commit()

    def remove_semester(self, name: str) -> None:
        cur = self._conn.cursor()
        # Delete subjects (cascade removes assignments/exams)
        cur.execute("DELETE FROM subjects WHERE semester_name=? AND year=?", (name, self.year))
        cur.execute("DELETE FROM semesters WHERE name=? AND year=?", (name, self.year))
        self._conn.commit()
        self.data = self.load_data()

    # Bulk helpers
    def add_semesters(self, names: List[str]) -> None:
        """Add multiple semesters in one transaction (ignores duplicates).

        Args:
            names: Iterable of semester names to insert for current year.
        """
        cleaned = [n.strip() for n in names if n and n.strip()]
        if not cleaned:
            return
        cur = self._conn.cursor()
        cur.executemany(
            "INSERT OR IGNORE INTO semesters(name, year) VALUES(?,?)",
            [(n, self.year) for n in cleaned],
        )
        self._conn.commit()

    def count_subjects_per_semester(self) -> List[tuple[str, int]]:
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT s.name, COUNT(sub.id) as cnt
            FROM (
                SELECT name FROM semesters WHERE year=?
                UNION
                SELECT DISTINCT semester_name AS name FROM subjects WHERE year=?
            ) s
            LEFT JOIN subjects sub ON sub.semester_name = s.name AND sub.year=?
            GROUP BY s.name
            ORDER BY s.name COLLATE NOCASE
            """,
            (self.year, self.year, self.year),
        )
        return [(r[0], r[1]) for r in cur.fetchall()]

    # --------- Subject CRUD / queries ---------
    def upsert_subject(self, semester: str, subject: Subject) -> None:
        # Insert-only semantics (no implicit modify): ignore duplicates, skip empty values
        code = (subject.subject_code or "").strip()
        name = (subject.subject_name or "").strip()
        if not code or not name:
            return  # Skip invalid
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO subjects(subject_code, subject_name, semester_name, year, total_mark, sync_subject)
            SELECT ?,?,?,?,?,?
            WHERE trim(?)<>'' AND trim(?)<>''
            """,
            (
                code,
                name,
                semester,
                self.year,
                subject.total_mark,
                1 if subject.sync_subject else 0,
                code,
                name,
            ),
        )
        self._conn.commit()
        if cur.rowcount:  # Only update cache if a new row was inserted
            self.data.setdefault(semester, {})[code] = subject

    def delete_subject(self, semester: str, subject_code: str) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "DELETE FROM subjects WHERE subject_code=? AND semester_name=? AND year=?",
            (subject_code, semester, self.year),
        )
        self._conn.commit()
        if semester in self.data and subject_code in self.data[semester]:
            del self.data[semester][subject_code]

    def set_total_mark(self, semester: str, subject_code: str, total_mark: float) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "UPDATE subjects SET total_mark=? WHERE subject_code=? AND semester_name=? AND year=?",
            (total_mark, subject_code, semester, self.year),
        )
        self._conn.commit()
        if semester in self.data and subject_code in self.data[semester]:
            self.data[semester][subject_code].total_mark = total_mark

    # --------- Assignment CRUD ---------
    def upsert_assignment(
        self,
        semester: str,
        subject_code: str,
        assessment: str,
        weighted_mark: Any,
        unweighted_mark: Any,
        mark_weight: Any,
        grade_type: GradeType,
    ) -> None:
        # Insert-only semantics: ignore duplicates and skip empty assessment
        assessment_clean = (assessment or "").strip()
        if not assessment_clean:
            return
        cur = self._conn.cursor()
        # Ensure subject shell exists (insert only; won't modify existing)
        cur.execute(
            "SELECT 1 FROM subjects WHERE subject_code=? AND semester_name=? AND year=?",
            (subject_code, semester, self.year),
        )
        if not cur.fetchone():
            subj = Subject(subject_code=subject_code, subject_name=subject_code)
            self.upsert_subject(semester, subj)
        cur.execute(
            """
            INSERT OR IGNORE INTO assignments(subject_code, semester_name, year, assessment, weighted_mark, unweighted_mark, mark_weight, grade_type)
            SELECT ?,?,?,?,?,?,?,?
            WHERE trim(?)<>''
            """,
            (
                subject_code,
                semester,
                self.year,
                assessment_clean,
                str(weighted_mark) if weighted_mark is not None else None,
                unweighted_mark,
                mark_weight,
                grade_type.value,
                assessment_clean,
            ),
        )
        self._conn.commit()
        if cur.rowcount:
            # Refresh cache only if insertion occurred
            self.data = self.load_data()

    def update_assignment(
        self,
        semester: str,
        subject_code: str,
        old_assessment: str,
        new_assessment: str,
        weighted_mark: Any,
        unweighted_mark: Any,
        mark_weight: Any,
        grade_type: GradeType,
    ) -> None:
        """Update an existing assignment row without deleting/inserting a new one.

        Falls back to insert (via upsert_assignment) if the assignment does not yet exist.
        """
        cur = self._conn.cursor()
        # Ensure subject exists
        cur.execute(
            "SELECT 1 FROM subjects WHERE subject_code=? AND semester_name=? AND year=?",
            (subject_code, semester, self.year),
        )
        if not cur.fetchone():
            subj = Subject(subject_code=subject_code, subject_name=subject_code)
            self.upsert_subject(semester, subj)
        cur.execute(
            """
            UPDATE assignments
            SET assessment=?, weighted_mark=?, unweighted_mark=?, mark_weight=?, grade_type=?
            WHERE subject_code=? AND semester_name=? AND year=? AND assessment=?
            """,
            (
                new_assessment,
                str(weighted_mark) if weighted_mark is not None else None,
                unweighted_mark,
                mark_weight,
                grade_type.value,
                subject_code,
                semester,
                self.year,
                old_assessment,
            ),
        )
        if cur.rowcount == 0:
            # Insert new row
            cur.execute(
                """
                INSERT INTO assignments(subject_code, semester_name, year, assessment, weighted_mark, unweighted_mark, mark_weight, grade_type)
                VALUES(?,?,?,?,?,?,?,?)
                """,
                (
                    subject_code,
                    semester,
                    self.year,
                    new_assessment,
                    str(weighted_mark) if weighted_mark is not None else None,
                    unweighted_mark,
                    mark_weight,
                    grade_type.value,
                ),
            )
        self._conn.commit()
        # Reload cache (simple approach for now)
        self.data = self.load_data()

    def delete_assignment(self, semester: str, subject_code: str, assessment: str) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "DELETE FROM assignments WHERE subject_code=? AND semester_name=? AND year=? AND assessment=?",
            (subject_code, semester, self.year, assessment),
        )
        self._conn.commit()
        self.data = self.load_data()

    # --------- Examination CRUD ---------
    def upsert_exam(self, semester: str, subject_code: str, exam_mark: float, exam_weight: float) -> None:
        """Insert or replace examination row for a subject.

        Creates the subject shell if it does not yet exist (mirrors assignment upsert behaviour).
        """
        cur = self._conn.cursor()
        # Ensure subject exists
        cur.execute(
            "SELECT 1 FROM subjects WHERE subject_code=? AND semester_name=? AND year=?",
            (subject_code, semester, self.year),
        )
        if not cur.fetchone():
            subj = Subject(subject_code=subject_code, subject_name=subject_code)
            self.upsert_subject(semester, subj)
        cur.execute(
            "DELETE FROM examinations WHERE subject_code=? AND semester_name=? AND year=?",
            (subject_code, semester, self.year),
        )
        cur.execute(
            "INSERT INTO examinations(subject_code, semester_name, year, exam_mark, exam_weight) VALUES(?,?,?,?,?)",
            (subject_code, semester, self.year, exam_mark, exam_weight),
        )
        self._conn.commit()
        # Refresh just that subject in cache (simplest: full reload for now)
        self.data = self.load_data()

    def delete_exam(self, semester: str, subject_code: str) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "DELETE FROM examinations WHERE subject_code=? AND semester_name=? AND year=?",
            (subject_code, semester, self.year),
        )
        self._conn.commit()
        self.data = self.load_data()

    # --------- Analytics queries ---------
    def fetch_subjects_for_analytics(self, current_semester: str, include_synced: bool = True) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        if include_synced:
            cur.execute(
                """
                WITH base AS (
                    SELECT subject_code, subject_name, semester_name, total_mark, sync_subject
                    FROM subjects WHERE year=?
                ), primary_sem AS (
                    SELECT * FROM base WHERE semester_name=?
                ), others AS (
                    SELECT * FROM base WHERE semester_name<>? AND sync_subject=1 AND subject_code NOT IN (
                        SELECT subject_code FROM primary_sem
                    )
                )
                SELECT * FROM primary_sem
                UNION ALL
                SELECT * FROM others
                ORDER BY semester_name, subject_code
                """,
                (self.year, current_semester, current_semester),
            )
        else:
            cur.execute(
                """
                SELECT subject_code, subject_name, semester_name, total_mark, sync_subject
                FROM subjects WHERE year=? AND semester_name=? ORDER BY subject_code
                """,
                (self.year, current_semester),
            )
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    # --- query helpers (DB-backed, bypass in-memory snapshot) ---
    def fetch_synced_subjects(self, exclude_semester: str) -> List[Subject]:
        """Return all subjects flagged for sync that are NOT in the excluded semester.

        This performs direct SQL queries so it always reflects the latest persisted
        state even if `self.data` has not been refreshed recently.
        """
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT subject_code, subject_name, semester_name, total_mark
            FROM subjects
            WHERE year = ? AND semester_name <> ? AND sync_subject = 1
            ORDER BY semester_name, subject_code
            """,
            (self.year, exclude_semester),
        )
        rows = cur.fetchall()
        subjects: list[Subject] = []
        for code, name, sem_name, total_mark in rows:
            cur.execute(
                "SELECT assessment, weighted_mark, unweighted_mark, mark_weight, grade_type FROM assignments WHERE subject_code=? AND semester_name=? AND year=? ORDER BY id",
                (code, sem_name, self.year),
            )
            assignments: List[Assignment] = []
            for a_row in cur.fetchall():
                grade_raw = a_row[4] or GradeType.NUMERIC.value
                try:
                    gtype = GradeType(grade_raw)
                except ValueError:
                    gtype = GradeType.NUMERIC
                wm_txt = a_row[1]
                if wm_txt in (GradeType.SATISFACTORY.value, GradeType.UNSATISFACTORY.value):
                    w_mark = wm_txt
                else:
                    try:
                        w_mark = float(wm_txt) if wm_txt is not None else 0.0
                    except ValueError:
                        w_mark = 0.0
                assignments.append(
                    Assignment(
                        subject_assessment=a_row[0],
                        weighted_mark=w_mark,
                        unweighted_mark=a_row[2],
                        mark_weight=a_row[3],
                        grade_type=gtype,
                    )
                )
            cur.execute(
                "SELECT exam_mark, exam_weight FROM examinations WHERE subject_code=? AND semester_name=? AND year=?",
                (code, sem_name, self.year),
            )
            exam_row = cur.fetchone()
            examination = Examination(exam_mark=exam_row[0], exam_weight=exam_row[1]) if exam_row else Examination()
            subjects.append(
                Subject(
                    subject_code=code,
                    subject_name=name,
                    assignments=assignments,
                    total_mark=total_mark,
                    examinations=examination,
                    sync_subject=True,
                )
            )
        return subjects

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass

    # Context manager support
    def __enter__(self) -> "DataPersistenceSQLite":  # noqa: D401
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401
        self.close()


__all__ = ["DataPersistenceSQLite"]
