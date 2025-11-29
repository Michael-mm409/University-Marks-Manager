from sqlmodel import Session, select, create_engine
from src.infrastructure.db.models import GradeScale
from src.core.services.grade_calculator import GradeCalculator

# Connect to DB (assuming sqlite for now based on file list, but let's check engine.py)
# Actually, I'll just use the GradeCalculator logic which takes a session.
# I need to setup the DB engine first.
from src.infrastructure.db.engine import engine

def verify():
    with Session(engine) as session:
        # Ensure table exists (usually done by alembic or init_db, but for this test I might need to create it if using sqlite and it's not migrated)
        # Since I modified models.py, the table won't exist in the actual DB unless I run migration.
        # But for this test, I can try to create it.
        GradeScale.metadata.create_all(engine)
        
        gc = GradeCalculator(session)
        scales = gc._get_grade_scales()
        print("Grade Scales:")
        for s in scales:
            print(f"{s.grade}: Min {s.min_mark}, GPA {s.gpa_point}")
            
        # Test calculation logic (mocking subjects is hard here without inserting)
        # But seeing the scales confirms the seeding works.

if __name__ == "__main__":
    verify()
