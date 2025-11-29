
from sqlmodel import Session, select, create_engine
from src.infrastructure.db.models import Assignment
from pathlib import Path
import os

# Setup engine (copying from engine.py logic roughly)
DB_PATH = Path("data/marks.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

try:
    with Session(engine) as session:
        print("Attempting to query Assignments...")
        statement = select(Assignment).limit(1)
        results = session.exec(statement).all()
        print("Query successful.")
        for res in results:
            print(res)
except Exception as e:
    print(f"Query failed: {e}")
