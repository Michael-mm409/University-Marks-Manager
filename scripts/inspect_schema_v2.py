import sys
import os
from sqlalchemy import create_engine, inspect

def inspect_schema():
    # Connection string based on .env and docker-compose
    # Host is localhost because port 5432 is forwarded
    url = "postgresql://Michael:Mickyb22*@localhost:5432/marks-manager-db"
    
    print(f"Connecting to database: {url}")
    try:
        engine = create_engine(url)
        inspector = inspect(engine)
        
        if inspector.has_table("grade_scales"):
            print("\nColumns in 'grade_scales' table:")
            columns = inspector.get_columns("grade_scales")
            for column in columns:
                print(f"- {column['name']} ({column['type']})")
        else:
            print("\nTable 'grade_scales' does not exist.")
            
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    inspect_schema()
