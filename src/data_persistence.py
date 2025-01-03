from os import makedirs, path
import json
from tkinter import messagebox
from typing import Dict, List, Union

class DataPersistence:
    def __init__(self, year: str, file_directory: str = './data'):
        """Initialize DataPersistence for a specific year and directory."""
        self.year: str = year
        self.file_directory: str = file_directory
        makedirs(self.file_directory, exist_ok=True)  # Ensure directory exists
        self.file_path = path.join(self.file_directory, f"{self.year}.json")
        self.data = self.load_data_from_json()

    def load_data_from_json(self) -> Dict[str, Dict[str, List[Dict[str, Union[str, float]]]]]:
        """Load data from the JSON file or return an empty structure if the file doesn't exist."""
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

    def save_data_to_json(self):
        """Save data to the JSON file."""
        with open(self.file_path, 'w', encoding='utf-8') as json_file:
                json.dump(self.data, json_file, indent=4)
        messagebox.showinfo("Success", f"Data saved successfully to {self.file_path}!")

    def sync_semesters(self):
        """Sync data between the Autumn, Spring, and Annual semesters."""
        # Only sync subjects that exist in the "Annual" semester
        if "Annual" in self.data:
            annual_data = self.data["Annual"]

            # Sync data from "Annual" to "Autumn"
            for subject, details in annual_data.items():
                self.data["Autumn"][subject] = details

            # Sync data from "Annual" to "Spring"
            for subject, details in annual_data.items():
                self.data["Spring"][subject] = details

        self.save_data_to_json()
