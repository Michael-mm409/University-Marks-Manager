"""
This module provides classes for data persistence in the University Marks Manager application (Streamlit version).
"""

import json
import os
from typing import Any, Dict, List

import streamlit as st

# Fix: Use relative import to avoid circular dependency
from model.domain.entities import Assignment, Examination, Subject

from ..enums.data_keys import DataKeys
from ..enums.grade_types import GradeType


class DataPersistence:
    """
    DataPersistence is a class responsible for managing the persistence of university marks data.
    """

    def __init__(self, year: str):
        self.year: str = year
        self.file_path: str = f"data/{year}.json"
        self.data: Dict[str, Dict[str, Subject]] = self.load_data()

    def _get_field_value(
        self, record: Dict[str, Any], current_key: DataKeys, legacy_key: DataKeys, default: Any = None
    ) -> Any:
        """Helper to get field value with fallback to legacy key."""
        return record.get(current_key.value, record.get(legacy_key.value, default))

    def load_data(self) -> Dict[str, Dict[str, Subject]]:
        """
        Load data from a JSON file and convert it into a structured dictionary of Subject objects.
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                raw_data: Dict[str, Dict[str, Any]] = json.load(file)
                data: Dict[str, Dict[str, Subject]] = {}

                for sem_name, subjects in raw_data.items():
                    data[sem_name] = {}

                    for subj_code, subj_dict in subjects.items():
                        assignment_list: List[Assignment] = []
                        assignment_records: List[Dict[str, Any]] = self._get_field_value(
                            subj_dict, DataKeys.ASSIGNMENTS, DataKeys.ASSIGNMENTS_LEGACY, []
                        )

                        for assignment_record in assignment_records:
                            # Handle grade_type conversion properly
                            grade_type_str = self._get_field_value(
                                assignment_record, DataKeys.GRADE_TYPE, DataKeys.GRADE_TYPE_LEGACY, "numeric"
                            )

                            try:
                                grade_type = GradeType(grade_type_str)
                            except ValueError:
                                grade_type = GradeType.NUMERIC

                            assignment = Assignment(
                                subject_assessment=self._get_field_value(
                                    assignment_record,
                                    DataKeys.SUBJECT_ASSESSMENT,
                                    DataKeys.SUBJECT_ASSESSMENT_LEGACY,
                                    "",
                                ),
                                weighted_mark=self._get_field_value(
                                    assignment_record, DataKeys.WEIGHTED_MARK, DataKeys.WEIGHTED_MARK_LEGACY, 0.0
                                ),
                                unweighted_mark=self._get_field_value(
                                    assignment_record, DataKeys.UNWEIGHTED_MARK, DataKeys.UNWEIGHTED_MARK_LEGACY, None
                                ),
                                mark_weight=self._get_field_value(
                                    assignment_record, DataKeys.MARK_WEIGHT, DataKeys.MARK_WEIGHT_LEGACY, None
                                ),
                                grade_type=grade_type,
                            )
                            assignment_list.append(assignment)

                        # Load examinations with proper typing
                        examinations_dict: Dict[str, Any] = self._get_field_value(
                            subj_dict, DataKeys.EXAMINATIONS, DataKeys.EXAMINATIONS_LEGACY, {}
                        )

                        examinations = Examination(
                            exam_mark=self._get_field_value(
                                examinations_dict, DataKeys.EXAM_MARK, DataKeys.EXAM_MARK_LEGACY, 0.0
                            ),
                            exam_weight=self._get_field_value(
                                examinations_dict, DataKeys.EXAM_WEIGHT, DataKeys.EXAM_WEIGHT_LEGACY, 100.0
                            ),
                        )

                        data[sem_name][subj_code] = Subject(
                            subject_code=subj_code,
                            subject_name=self._get_field_value(
                                subj_dict, DataKeys.SUBJECT_NAME, DataKeys.SUBJECT_NAME_LEGACY, "N/A"
                            ),
                            assignments=assignment_list,
                            total_mark=self._get_field_value(
                                subj_dict, DataKeys.TOTAL_MARK, DataKeys.TOTAL_MARK_LEGACY, 0.0
                            ),
                            examinations=examinations,
                            sync_subject=self._get_field_value(
                                subj_dict, DataKeys.SYNC_SUBJECT, DataKeys.SYNC_SUBJECT_LEGACY, False
                            ),
                        )
                return data
        else:
            return {}

    def save_data(self, semesters: Dict[str, Dict[str, Subject]]) -> None:
        """
        Saves semester data to a JSON file at the specified file path.
        """
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            serializable_data: Dict[str, Dict[str, Any]] = {}

            for sem_name, subjects in semesters.items():
                if isinstance(subjects, dict):
                    serializable_data[sem_name] = {
                        subj_code: subject.model_dump() for subj_code, subject in subjects.items()
                    }
                else:
                    st.warning(f"Semester '{sem_name}' does not contain a dict of subjects. Skipping.")

            with open(self.file_path, "w") as file:
                json.dump(serializable_data, file, indent=4)
        except (IOError, json.JSONDecodeError) as e:
            st.error(f"Failed to save data: {e}")
