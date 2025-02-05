import json
from os import makedirs, path
from tinydb import TinyDB
from tkinter import messagebox
from typing import Dict, List, Union


class PrettyStorage:
    """Custom storage class to pretty print JSON data."""
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        if path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        else:
            return {}

    def write(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)  # Pretty print with indentation


class DataPersistence:
    def __init__(self, year: str, file_directory: str = './data', use_tinydb: bool = False):
        """Initialize DataPersistence for a specific year and directory, optionally using MongoDB."""
        self.year: str = year
        self.file_directory: str = file_directory
        self.use_tinydb = use_tinydb

        # TinyDB setup
        if self.use_tinydb:
            self.db_path = path.join(self.file_directory, f"{self.year}.json")
            makedirs(self.file_directory, exist_ok=True)  # Ensure directory exists

            self.db = TinyDB(self.db_path, storage=PrettyStorage)  # Use PrettyStorage for formatted output
            self.data_table = self.db.table("semester_data")  # Create a table if it doesn't exist
        else:
            self.file_path = path.join(self.file_directory, f"{self.year}.json")
            makedirs(self.file_directory, exist_ok=True)  # Ensure directory exists

        self.data = self.load_data()

    def load_data(self) -> Dict[str, Dict[str, List[Dict[str, Union[str, float]]]]]:
        """Load data from TinyDB or from a JSON file."""
        if self.use_tinydb:
            # TinyDB: Fetch the data or initialize if the data doesn't exist
            data_entry = self.data_table.get(doc_id=1)  # We use doc_id=1 as a single entry for simplicity
            if data_entry:
                return data_entry["semester_data"]
            else:
                # Initialize structure for all semesters (Autumn, Spring, Annual)
                return {
                    "Autumn": {},
                    "Spring": {},
                    "Annual": {}
                }
        else:
            # JSON file: Load data from a JSON file
            if path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as json_file:
                    return json.load(json_file)
            else:
                # Initialize structure for all semesters (Autumn, Spring, Annual)
                return {
                    "Autumn": {},
                    "Spring": {},
                    "Annual": {}
                }

    def save_data(self):
        """Save data to TinyDB or JSON file with pretty-printing."""
        if self.use_tinydb:
            # Check if data already exists in the database (based on a unique year or identifier)
            existing_entry = self.data_table.search(lambda doc: doc.get("year") == self.year)

            if existing_entry:
                # If the entry exists, update it
                self.data_table.update({"semester_data": self.data}, doc_ids=[existing_entry[0].doc_id])
            else:
                # If no entry exists, insert the new data
                self.data_table.insert({"year": self.year, "semester_data": self.data})

        else:
            # JSON file: Save data to a JSON file with pretty printing
            with open(self.file_path, 'w', encoding='utf-8') as json_file:
                json.dump(self.data, json_file, indent=4)
            messagebox.showinfo("Success", f"Data saved successfully to {self.file_path}!")

    def sync_semesters(self):
        """Sync data between the Autumn, Spring, and Annual semesters."""
        if "Annual" in self.data:
            print("Annual exists in the data!")
            annual_data = self.data["Annual"]

            # Sync data from "Annual" to "Autumn"
            for subject, details in annual_data.items():
                self.data["Autumn"][subject] = details

            # Sync data from "Annual" to "Spring"
            for subject, details in annual_data.items():
                self.data["Spring"][subject] = details

        self.save_data()
