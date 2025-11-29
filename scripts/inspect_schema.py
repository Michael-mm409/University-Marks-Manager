import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, inspect
from src.infrastructure.db.engine import get_db_url

def inspect_schema():
    url = get_db_url()
    print(f"Connecting to database: {url}")
    engine = create_engine(url)
    inspector = inspect(engine)
    
    if inspector.has_table("grade_scales"):
        print("\nColumns in 'grade_scales' table:")
        columns = inspector.get_columns("grade_scales")
        for column in columns:
            print(f"- {column['name']} ({column['type']})")
    else:
        print("\nTable 'grade_scales' does not exist.")

if __name__ == "__main__":
    inspect_schema()
