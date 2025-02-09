"""
This module provides classes for data persistence in the University Marks Manager application.
"""
import json
from os import makedirs, path
from tkinter import messagebox
from typing import Dict, List, Union

class DataPersistence:
    """The DataPersistence class is responsible for loading and saving data to a JSON file."""
    def __init__(self, year: str, file_directory: str = './data'):
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
        try:
            with open(self.file_path, 'w', encoding='utf-8') as json_file:
                json.dump(self.data, json_file, indent=4)
            messagebox.showinfo("Success", f"Data saved successfully to {self.file_path}!")
        except (IOError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
