import time
from src.infrastructure.db.engine import engine
from src.infrastructure.db.models import SQLModel, Semester, Subject, Assignment

def main():
    print("Attempting to connect to the database...")
    # Give the database a moment to start up
    time.sleep(5)
    
    try:
        # The engine is already created in engine.py
        # This will attempt to connect to the database
        with engine.connect() as connection:
            print("Database connection successful.")
            print("Creating tables...")
            SQLModel.metadata.create_all(engine)
            print("Tables created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your database connection settings and ensure the database container is running.")

if __name__ == "__main__":
    main()
