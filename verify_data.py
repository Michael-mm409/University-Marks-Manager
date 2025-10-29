import os
import sys
from sqlmodel import Session, select
from sqlalchemy import create_engine

# Add the src directory to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.infrastructure.db.models import Semester

POSTGRES_DATABASE_URL = os.getenv("DATABASE_URL")

def verify_data():
    """
    Connects to the PostgreSQL database and prints the contents of the Semester table.
    """
    if not POSTGRES_DATABASE_URL:
        print("Error: DATABASE_URL environment variable is not set.")
        return

    print("Connecting to PostgreSQL to verify data...")
    engine = create_engine(POSTGRES_DATABASE_URL, echo=False)

    with Session(engine) as session:
        print("Fetching semesters from the database...")
        semesters = session.exec(select(Semester)).all()

        if not semesters:
            print("\\n--- No semesters found in the database. ---")
        else:
            print(f"\\n--- Found {len(semesters)} semesters: ---")
            for semester in semesters:
                print(semester)

if __name__ == "__main__":
    verify_data()
