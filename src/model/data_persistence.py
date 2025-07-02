"""
This module provides classes for data persistence in the University Marks Manager application (Streamlit version).
"""

import json
import os
from typing import Dict

import streamlit as st  # <-- Use Streamlit for feedback

from model.enums import DataKeys
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
                        assignment_list = []
                        assignment_records = subj_dict.get(
                            DataKeys.ASSIGNMENTS.value, subj_dict.get(DataKeys.ASSIGNMENTS_LEGACY.value, [])
                        )
                        for assignment_record in assignment_records:
                            assignment = Assignment(
                                subject_assessment=assignment_record.get(
                                    DataKeys.SUBJECT_ASSESSMENT.value,
                                    assignment_record.get(DataKeys.SUBJECT_ASSESSMENT_LEGACY.value, ""),
                                ),
                                weighted_mark=assignment_record.get(
                                    DataKeys.WEIGHTED_MARK.value,
                                    assignment_record.get(DataKeys.WEIGHTED_MARK_LEGACY.value, 0.0),
                                ),
                                unweighted_mark=assignment_record.get(
                                    DataKeys.UNWEIGHTED_MARK.value,
                                    assignment_record.get(DataKeys.UNWEIGHTED_MARK_LEGACY.value, None),
                                ),
                                mark_weight=assignment_record.get(
                                    DataKeys.MARK_WEIGHT.value,
                                    assignment_record.get(DataKeys.MARK_WEIGHT_LEGACY.value, None),
                                ),
                                grade_type=assignment_record.get("grade_type", "numeric"),
                            )
                            assignment_list.append(assignment)

                        # Load examinations
                        examinations_dict = subj_dict.get(DataKeys.EXAMINATIONS) or subj_dict.get(
                            DataKeys.EXAMINATIONS_LEGACY, {}
                        )
                        examinations = Examination(
                            exam_mark=examinations_dict.get(
                                DataKeys.EXAM_MARK, examinations_dict.get(DataKeys.EXAM_MARK_LEGACY, 0.0)
                            ),
                            exam_weight=examinations_dict.get(
                                DataKeys.EXAM_WEIGHT, examinations_dict.get(DataKeys.EXAM_WEIGHT_LEGACY, 100.0)
                            ),
                        )
                        data[sem_name][subj_code] = Subject(
                            subject_code=subj_code,
                            subject_name=subj_dict.get(DataKeys.SUBJECT_NAME.value)
                            or subj_dict.get(DataKeys.SUBJECT_NAME_LEGACY, "N/A"),
                            assignments=assignment_list,
                            total_mark=subj_dict.get(
                                DataKeys.TOTAL_MARK.value, subj_dict.get(DataKeys.TOTAL_MARK_LEGACY.value, 0.0)
                            ),
                            examinations=examinations,
                            sync_subject=subj_dict.get(
                                DataKeys.SYNC_SUBJECT.value, subj_dict.get(DataKeys.SYNC_SUBJECT_LEGACY.value, False)
                            ),
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
                        subj_code: subject.model_dump()  # Changed from asdict() to model_dump()
                        for subj_code, subject in subjects.items()
                    }
                else:
                    st.warning(f"Semester '{sem_name}' does not contain a dict of subjects. Skipping.")
            with open(self.file_path, "w") as file:
                json.dump(serializable_data, file, indent=4)
        except (IOError, json.JSONDecodeError) as e:
            st.error(f"Failed to save data: {e}")
