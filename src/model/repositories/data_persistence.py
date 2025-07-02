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
    The `DataPersistence` class is responsible for managing the loading and saving of semester data
    to and from JSON files. It provides methods to deserialize JSON data into structured Python objects
    and serialize Python objects back into JSON format.

    Args:
        year (str): The academic year for which the data is being managed.
        file_path (str): The file path to the JSON file where the data is stored.
        data (Dict[str, Dict[str, Subject]]): A dictionary containing the loaded semester data.

    Methods:
        __init__(year: str):
            Initializes the `DataPersistence` instance with the specified academic year.
        _get_field_value(record: Dict[str, Any], current_key: DataKeys, legacy_key: DataKeys, default: Any = None) -> Any:
            Helper method to retrieve a field value from a record, with a fallback to a legacy key if the current key is not found.
        load_data() -> Dict[str, Dict[str, Subject]]:
            Loads data from the JSON file specified by `file_path` and converts it into a structured dictionary of `Subject` objects.
        save_data(semesters: Dict[str, Dict[str, Subject]]) -> None:
            Saves the provided semester data to the JSON file specified by `file_path`.
    """

    def __init__(self, year: str):
        self.year: str = year
        self.file_path: str = f"data/{year}.json"
        self.data: Dict[str, Dict[str, Subject]] = self.load_data()

    def _get_field_value(
        self, record: Dict[str, Any], current_key: DataKeys, legacy_key: DataKeys, default: Any = None
    ) -> Any:
        """
        Retrieves the value of a specified field from a record dictionary, checking both
        a current key and a legacy key, and returning a default value if neither key exists.
        Args:
            record (Dict[str, Any]): The dictionary containing the data record.
            current_key (DataKeys): The primary key to look for in the record.
            legacy_key (DataKeys): The fallback key to look for if the primary key is not found.
            default (Any, optional): The value to return if neither key is found. Defaults to None.
        Returns:
            Any: The value associated with the current key or legacy key, or the default value
            if neither key exists in the record.
        """

        return record.get(current_key.value, record.get(legacy_key.value, default))

    def load_data(self) -> Dict[str, Dict[str, Subject]]:
        """
        Loads data from a JSON file and deserializes it into a nested dictionary structure.
        The method reads the file specified by `self.file_path` and parses its contents
        into a dictionary where the keys are semester names and the values are dictionaries
        of subjects. Each subject contains its associated assignments, examinations, and
        other metadata.

        Returns:
            Dict[str, Dict[str, Subject]]: A dictionary where:
                - The outer keys are semester names (e.g., "Spring 2023").
                - The inner keys are subject codes (e.g., "CSCI123").
                - The values are `Subject` objects containing detailed information about
                  the subject, including assignments, examinations, and marks.

        Notes:
            - If the file does not exist, an empty dictionary is returned.
            - Legacy keys are supported for backward compatibility.
            - Invalid `GradeType` values default to `GradeType.NUMERIC`.

        Raises:
            ValueError: If the JSON file contains invalid data that cannot be parsed.
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
        Saves the provided semester data to a JSON file. This method serializes the semester data, ensuring that each subject's data is converted into a serializable format using the `model_dump` method. The serialized data is then written to a file specified by `self.file_path`.

        Args:
            semesters (Dict[str, Dict[str, Subject]]): A dictionary where the keys
                are semester names and the values are dictionaries of subjects. Each
                subject dictionary maps subject codes to `Subject` objects.

        Raises:
            IOError: If there is an issue creating directories or writing to the file.
            json.JSONDecodeError: If there is an error during JSON serialization.

        Notes:
            - If a semester does not contain a dictionary of subjects, it will be
            skipped, and a warning will be displayed using `st.warning`.
            - Any errors encountered during the save process will be displayed using
            `st.error`.
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
