import os
import sys
from sqlalchemy import create_engine, text, inspect

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fix_schema():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set. Please run this inside the container or set the variable.")
        return

    print(f"Connecting to database...")
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        
        # 1. Check subjects.credit_points
        if "subjects" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("subjects")]
            if "credit_points" not in cols:
                print("Adding credit_points to subjects...")
                conn.execute(text("ALTER TABLE subjects ADD COLUMN credit_points INTEGER DEFAULT 6"))
                conn.commit()
                print("Added credit_points.")
            else:
                print("subjects.credit_points exists.")
        
        # 2. Check assignments.is_exam
        if "assignments" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("assignments")]
            if "is_exam" not in cols:
                print("Adding is_exam to assignments...")
                conn.execute(text("ALTER TABLE assignments ADD COLUMN is_exam BOOLEAN DEFAULT FALSE"))
                conn.commit()
                print("Added is_exam.")
            else:
                print("assignments.is_exam exists.")

        # 3. Check grade_scales.id
        if "grade_scales" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("grade_scales")]
            if "id" not in cols:
                print("Adding id to grade_scales...")
                
                # Check for existing primary key
                pk_constraint = inspector.get_pk_constraint("grade_scales")
                if pk_constraint and pk_constraint['constrained_columns']:
                    print(f"Found existing PK: {pk_constraint['name']} on {pk_constraint['constrained_columns']}")
                    # Drop existing PK
                    conn.execute(text(f"ALTER TABLE grade_scales DROP CONSTRAINT {pk_constraint['name']}"))
                    print("Dropped existing PK constraint.")

                # This is Postgres specific for adding a primary key serial column
                conn.execute(text("ALTER TABLE grade_scales ADD COLUMN id SERIAL PRIMARY KEY"))
                conn.commit()
                print("Added id to grade_scales.")
            else:
                print("grade_scales.id exists.")

        # 4. Check grade_scales.scale_name
        if "grade_scales" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("grade_scales")]
            if "scale_name" not in cols:
                print("Adding scale_name to grade_scales...")
                conn.execute(text("ALTER TABLE grade_scales ADD COLUMN scale_name VARCHAR DEFAULT 'Standard'"))
                # Create index if it doesn't exist (though SQLModel usually handles this, we are patching manually)
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_grade_scales_scale_name ON grade_scales (scale_name)"))
                conn.commit()
                print("Added scale_name to grade_scales.")
            else:
                print("grade_scales.scale_name exists.")

        # 5. Check courses.grading_scale
        if "courses" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("courses")]
            if "grading_scale" not in cols:
                print("Adding grading_scale to courses...")
                conn.execute(text("ALTER TABLE courses ADD COLUMN grading_scale VARCHAR DEFAULT 'Standard'"))
                conn.commit()
                print("Added grading_scale to courses.")
            else:
                print("courses.grading_scale exists.")

if __name__ == "__main__":
    fix_schema()
