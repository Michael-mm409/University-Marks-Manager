"""
This module provides classes for data persistence in the University Marks Manager application.
"""
import json
import logging
from os import makedirs, path
from typing import Dict, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataPersistence:
    """The DataPersistence class is responsible for loading and saving data to a JSON file."""
    def __init__(self, year: str, file_directory: str = './data'):
        self.year: str = year
        self.file_directory: str = file_directory

        self.file_path = path.join(self.file_directory, f"{self.year}.json")
        makedirs(self.file_directory, exist_ok=True)  # Ensure directory exists

        self.data = self.load_data()

    def load_data(self) -> Dict[str, Dict[str, List[Dict[str, Union[str, float]]]]]:
        """Load data from a JSON file."""
        if path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as json_file:
                    return json.load(json_file)
            except (json.JSONDecodeError, IOError) as error:
                logging.error(f"Error reading {self.file_path}: {error}. Initialising with empty data.")
        else:
            logging.info(f"{self.file_path} does not exist. Initialising with empty data.")
        
        # Initialize structure for all semesters (Autumn, Spring, Annual)
        return {
            "Autumn": {},
            "Spring": {},
            "Annual": {}
        }

    def save_data(self):
        """Save data to JSON file with pretty-printing."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as json_file:
                json.dump(self.data, json_file, indent=4)
            logging.info(f"Data saved successfully to {self.file_path}")
        except IOError as error:
            logging.error(f"Error saving data: {error}")

    def add_semester(self, semester_name: str) -> None:
        """Add a new semester to the data structure."""
        if semester_name not in self.data:
            self.data[semester_name] = {}
            self.save_data()
            logging.info(f"Semester '{semester_name}' added.")

    def remove_semester(self, semester_name: str) -> None:
        """Remove a semester from the data structure."""
        if semester_name in self.data:
            del self.data[semester_name]
            self.save_data()
            logging.info(f"Semester '{semester_name}' removed.")