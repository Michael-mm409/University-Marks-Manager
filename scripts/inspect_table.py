import os
import sys
from sqlalchemy import create_engine, inspect

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def inspect_table():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set.")
        return

    print(f"Connecting to database...")
    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    table_name = "grade_scales"
    if inspector.has_table(table_name):
        print(f"\nTable '{table_name}' exists.")
        
        print("\nColumns:")
        for col in inspector.get_columns(table_name):
            print(f"- {col['name']} ({col['type']})")
            
        print("\nPrimary Keys:")
        pk = inspector.get_pk_constraint(table_name)
        print(pk)
        
        print("\nUnique Constraints:")
        for uc in inspector.get_unique_constraints(table_name):
            print(uc)
    else:
        print(f"\nTable '{table_name}' does not exist.")

if __name__ == "__main__":
    inspect_table()
