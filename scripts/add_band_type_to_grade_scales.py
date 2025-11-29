"""
Migration script to add band_type column to grade_scales table for WAM/GPA separation.
"""
import sqlalchemy as sa
from sqlalchemy.engine import create_engine

# Adjust these as needed for your environment
DB_URL = "postgresql://Michael:Mickyb22*@marks-manager-db:5432/marks-manager-db"
def main():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        # Add band_type column if it doesn't exist
        result = conn.execute(sa.text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='grade_scales' AND column_name='band_type';
        """))
        if not result.fetchone():
            print("Adding band_type column to grade_scales...")
            conn.execute(sa.text("""
                ALTER TABLE grade_scales ADD COLUMN band_type VARCHAR(8) DEFAULT 'both';
            """))
            print("band_type column added.")
        else:
            print("band_type column already exists.")

        # Update all existing rows to 'both'
        conn.execute(sa.text("""
            UPDATE grade_scales SET band_type = 'both' WHERE band_type IS NULL;
        """))
        print("All existing grade_scales rows set to band_type='both'.")

if __name__ == "__main__":
    main()
