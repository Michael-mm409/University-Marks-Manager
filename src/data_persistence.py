import json
from os import makedirs, path
from tinydb import TinyDB, Query
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
    def __init__(self, year: str, file_directory: str = './data'):
        """Initialize DataPersistence for a specific year and directory, optionally using MongoDB."""
        self.year: str = year
        self.file_directory: str = file_directory
    
        self.file_path = path.join(self.file_directory, f"{self.year}.json")
        makedirs(self.file_directory, exist_ok=True)  # Ensure directory exists

        self.data = self.load_data()


    def load_data(self) -> Dict[str, Dict[str, List[Dict[str, Union[str, float]]]]]:
        """Load data from TinyDB or from a JSON file."""
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
              
        with open(self.file_path, 'w', encoding='utf-8') as json_file:
            json.dump(self.data, json_file, indent=4)
        messagebox.showinfo("Success", f"Data saved successfully to {self.file_path}!")
