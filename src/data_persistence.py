"""
This module provides classes for data persistence in the University Marks Manager application.
"""

import json
import os
from dataclasses import asdict, is_dataclass

from PyQt6.QtWidgets import QMessageBox

from models import Assignment, Examination, Subject


class DataPersistence:
    """
    DataPersistence is a class responsible for managing the persistence of university marks data.
    It provides functionality to load and save structured data from and to JSON files, enabling
    the organization of semesters, subjects, assignments, and examinations.
    Args:
        year (str): The academic year for which data is being managed.
        file_path (str): The file path to the JSON file where data is stored.
        data (dict): A dictionary containing the loaded data, structured by semesters and subjects.
    Methods:
        __init__(year: str):
            Initializes the DataPersistence instance with the specified academic year.
            Automatically loads data from the corresponding JSON file.
        load_data() -> dict:
            Loads data from the JSON file specified by `self.file_path`.
            Converts raw JSON data into structured dictionaries of Subject objects.
            Handles variations in key names and provides default values for missing keys.
                dict: A dictionary structured by semesters and subjects.
        save_data(semesters: dict):
            Saves the current data to the JSON file specified by `self.file_path`.
            Converts Subject objects into serializable dictionaries before saving.
            Handles errors related to file I/O and JSON encoding.
            Args:
                semesters (dict): A dictionary containing semester data to be saved.
    """

    def __init__(self, year: str):
        self.year = year
        self.file_path = f"data/{year}.json"
        self.data = self.load_data()

    def load_data(self) -> dict:
        """
        Load data from a JSON file and convert it into a structured dictionary of Subject objects.
        This method reads the JSON file specified by `self.file_path` and parses its contents.
        It converts the raw data into a dictionary where each semester name maps to another
        dictionary of subjects. Each subject is represented as a `Subject` object, containing
        assignments, examinations, and other relevant details.
        Returns:
            dict: A dictionary structured as follows:
                {
                    "semester_name": {
                        "subject_code": Subject(
                            subject_code="...",
                            subject_name="...",
                            assignments=[Assignment(...), ...],
                            total_mark=...,
                            examinations=Examination(...),
                            sync_subject=...
                        ...
                    },
                    ...
                }
                If the file does not exist, an empty dictionary is returned.
        Raises:
            JSONDecodeError: If the file exists but contains invalid JSON data.
        Notes:
            - The method handles variations in key names (e.g., "subject_name" vs "Subject Name").
            - If certain keys are missing, default values are used (e.g., "N/A" for subject name).
        """

        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                raw_data = json.load(file)
                # Convert dicts to Subject objects
                data = {}
                for sem_name, subjects in raw_data.items():
                    data[sem_name] = {}
                    for subj_code, subj_dict in subjects.items():
                        # print(subj_dict)
                        assignments = [
                            Assignment(
                                subject_assessment=assignment_record.get("subject_assessment")
                                or assignment_record.get("Subject Assessment")
                                or "",
                                unweighted_mark=assignment_record.get(
                                    "unweighted_mark", assignment_record.get("Unweighted Mark", 0.0)
                                ),
                                weighted_mark=assignment_record.get(
                                    "weighted_mark", assignment_record.get("Weighted Mark", 0.0)
                                ),
                                mark_weight=assignment_record.get(
                                    "mark_weight", assignment_record.get("Mark Weight", 0.0)
                                ),
                            )
                            for assignment_record in subj_dict.get("assignments", subj_dict.get("Assignments", []))
                        ]
                        examinations_dict = subj_dict.get("examinations") or subj_dict.get("Examinations", {})
                        examinations = Examination(
                            exam_mark=examinations_dict.get("exam_mark", examinations_dict.get("Exam Mark", 0.0)),
                            exam_weight=examinations_dict.get(
                                "exam_weight", examinations_dict.get("Exam Weight", 100.0)
                            ),
                        )
                        data[sem_name][subj_code] = Subject(
                            subject_code=subj_code,
                            subject_name=subj_dict.get("subject_name") or subj_dict.get("Subject Name") or "N/A",
                            assignments=assignments,
                            total_mark=subj_dict.get("total_mark", subj_dict.get("Total Mark", 0.0)),
                            examinations=examinations,
                            sync_subject=subj_dict.get("sync_subject", subj_dict.get("Sync Subject", False)),
                        )
                return data
        else:
            return {}

    def save_data(self, semesters: dict):
        """
        Saves semester data to a JSON file at the specified file path.
        This method serializes the provided semester data, ensuring that any
        dataclass objects are converted to dictionaries, and writes the data
        to a file in JSON format. If the directory for the file path does not
        exist, it will be created.
        Args:
            semesters (dict): A dictionary where keys are semester names and
                              values are dictionaries of subjects. Each subject
                              can be a dataclass or a regular object.
        Raises:
            IOError: If there is an issue creating the directory or writing to the file.
            json.JSONDecodeError: If there is an issue serializing the data to JSON.
        Notes:
            - If a semester does not contain a dictionary of subjects, it will be skipped
              with a warning message.
            - The file will be created or overwritten at the specified file path.
        """

        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            serializable_data = {}
            for sem_name, subjects in semesters.items():
                if isinstance(subjects, dict):
                    serializable_data[sem_name] = {
                        subj_code: asdict(subject)
                        if is_dataclass(subject) and not isinstance(subject, type)
                        else subject
                        for subj_code, subject in subjects.items()
                    }
                else:
                    QMessageBox.warning(
                        None, "Warning", f"Semester '{sem_name}' does not contain a dict of subjects. Skipping."
                    )
            with open(self.file_path, "w") as file:
                json.dump(serializable_data, file, indent=4)
        except (IOError, json.JSONDecodeError) as e:
            QMessageBox.critical(None, "Error", f"Failed to save data: {e}")
