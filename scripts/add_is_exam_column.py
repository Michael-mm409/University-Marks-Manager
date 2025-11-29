"""
Add is_exam column to assignments table.

Usage:
    python -m scripts.add_is_exam_column
"""
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
    return bool(res.first())

def main():
    with Session(engine) as session:
        print("Checking for 'is_exam' column in 'assignments' table...")
        if not column_exists(session, "assignments", "is_exam"):
            print("Adding 'is_exam' column...")
            session.execute(text("ALTER TABLE assignments ADD COLUMN is_exam BOOLEAN DEFAULT FALSE"))
            session.commit()
            print("Column added successfully.")
        else:
            print("'is_exam' column already exists.")

if __name__ == "__main__":
    main()
