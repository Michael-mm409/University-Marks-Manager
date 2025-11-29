import sys
import os
from sqlmodel import Session, text, select

from src.infrastructure.db.models import Subject

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.db.engine import engine

def add_credit_points_column():
    with Session(engine) as session:
        try:
            query = select(Subject.credit_points).limit(1)
            # Check if column exists
            session.exec(query)
            print("Column 'credit_points' already exists.")
        except Exception:
            session.rollback()
            print("Adding 'credit_points' column to subjects table...")
            session.execute(text("ALTER TABLE subjects ADD COLUMN credit_points INTEGER DEFAULT 6"))
            session.commit()
            print("Column added successfully.")

if __name__ == "__main__":
    add_credit_points_column()
