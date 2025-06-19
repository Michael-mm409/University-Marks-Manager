"""
This module provides classes for data persistence in the University Marks Manager application (Streamlit version).
"""

import json
import os
from dataclasses import asdict, is_dataclass
from typing import Dict

import streamlit as st  # <-- Use Streamlit for feedback

from model.models import Assignment, Examination, Subject


class DataPersistence:
    """
    DataPersistence is a class responsible for managing the persistence of university marks data.
    It provides functionality to load and save structured data from and to JSON files, enabling
    the organization of semesters, subjects, assignments, and examinations.
    """

    year: str
    file_path: str
    data: Dict[str, Dict[str, Subject]]

    def __init__(self, year: str):
        self.year: str = year
        self.file_path: str = f"data/{year}.json"
        self.data: Dict[str, Dict[str, Subject]] = self.load_data()

    def load_data(self) -> Dict[str, Dict[str, Subject]]:
        """
        Load data from a JSON file and convert it into a structured dictionary of Subject objects.
        Returns:
            dict: A dictionary structured by semesters and subjects.
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                raw_data = json.load(file)
                data = {}
                for sem_name, subjects in raw_data.items():
                    data[sem_name] = {}
                    for subj_code, subj_dict in subjects.items():
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

    def save_data(self, semesters: Dict[str, Dict[str, Subject]]) -> None:
        """
        Saves semester data to a JSON file at the specified file path.
        Uses Streamlit for error/warning messages.
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
                    st.warning(f"Semester '{sem_name}' does not contain a dict of subjects. Skipping.")
            with open(self.file_path, "w") as file:
                json.dump(serializable_data, file, indent=4)
        except (IOError, json.JSONDecodeError) as e:
            st.error(f"Failed to save data: {e}")
