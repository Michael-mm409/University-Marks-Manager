"""
This module provides classes for data persistence in the University Marks Manager application.
"""
import json
import os
from tkinter import messagebox
from typing import Dict, List, Union


class DataPersistence:
    """The DataPersistence class is responsible for loading and saving data to a JSON file."""
    def __init__(self, year: str):
        self.year = year
        self.file_path = f"data/{year}.json"
        self.data = self.load_data()

    def load_data(self) -> Dict[str, Dict[str, List[Dict[str, Union[str, float]]]]]:
        """Load data from the JSON file or initialize an empty dictionary if the file does not exist."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                return json.load(file)
        else:
            # Initialize an empty dictionary if the file does not exist
            return {}

    def save_data(self):
        """Save the current data to the JSON file."""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w") as file:
                json.dump(self.data, file, indent=4)
            messagebox.showinfo("Success", f"Data saved successfully to {self.file_path}!")
        except (IOError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
