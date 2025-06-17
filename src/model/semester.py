"""
This module provides the Semester class for managing data related to a specific semester
in the University Marks Manager application.

The Semester class is responsible for handling assignments and examinations for a given semester.
"""

from collections import OrderedDict
from typing import Any, Dict, Literal, Optional, Union

from PyQt6.QtWidgets import QMessageBox

from .data_persistence import DataPersistence
from .models import Assignment, Examination, Subject


class Semester:
    """
    A class to represent a semester in the University Marks Manager application.

    This class is responsible for managing the data related to a specific semester,
    including assignments and examinations.

    Args:
        name (str):
            The name of the semester (e.g., "Autumn", "Spring").
        year (str):
            The academic year for the semester.
        data_persistence (DataPersistence):
            An instance of the DataPersistence class for managing data storage and retrieval.
    """

    def __init__(self, name: str, year: str, data_persistence: DataPersistence):
        """
        Initializes a Semester instance.
        Args:
            name (str): The name of the semester (e.g., "Spring", "Fall").
            year (str): The year associated with the semester (e.g., "2023").
            data_persistence (DataPersistence): An instance of DataPersistence used to manage
                persistent data storage and retrieval.
        Attributes:
            name (str): The name of the semester.
            year (str): The year associated with the semester.
            data_persistence (DataPersistence): The data persistence instance for managing data.
            subjects (Dict[str, Subject]): A dictionary of subjects associated with the semester,
                initialized from the data persistence layer if available.
        """

        self.name = name
        self.year = year
        self.data_persistence = data_persistence
        # Initialize subjects from loaded data if available
        # Ensure all loaded subjects are Subject instances, not raw dicts
        loaded_subjects = self.data_persistence.data.get(self.name, {})
        self.subjects: Dict[str, Subject] = {}
        for code, subj in loaded_subjects.items():
            if isinstance(subj, Subject):
                self.subjects[code] = subj
            elif isinstance(subj, dict):
                # Convert assignments
                assignments = [
                    a if isinstance(a, Assignment) else Assignment(**a)
                    for a in subj.get("assignments", subj.get("Assignments", []))
                ]
                # Convert examinations
                examinations = subj.get("examinations", subj.get("Examinations", None))
                if examinations and isinstance(examinations, dict):
                    examinations = Examination(**examinations)
                elif not examinations:
                    examinations = Examination()
                self.subjects[code] = Subject(
                    subject_code=subj.get("subject_code", code),
                    subject_name=subj.get("subject_name", subj.get("Subject Name", "N/A")),
                    assignments=assignments,
                    total_mark=subj.get("total_mark", subj.get("Total Mark", 0)),
                    examinations=examinations,
                    sync_subject=subj.get("sync_subject", subj.get("Sync Subject", False)),
                )

    def get_subject_data(self, subject_code: str, subject_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves or initializes subject data for a given subject code within the semester.

        If the subject data does not exist in the persistence layer, it initializes the subject
        with default values. If the subject data already exists, it optionally updates the subject
        name if provided and different from the existing one.

        Args:
            subject_code (str): The unique code identifying the subject.
            subject_name (Optional[str]): The name of the subject. Defaults to None. If not provided,
                          "N/A" will be used as the default name.

        Returns:
            Dict[str, Any]: A dictionary containing the subject data, including assignments,
                    total marks, examinations, and other relevant information.
        """
        if self.name not in self.data_persistence.data:
            self.data_persistence.data[self.name] = {}

        if subject_code not in self.data_persistence.data[self.name]:
            self.data_persistence.data[self.name][subject_code] = Subject(
                subject_code=subject_code,
                subject_name=self.data_persistence.data[self.name][subject_code].get(
                    "Subject Name", subject_name or "N/A"
                ),
                assignments=[],
                total_mark=0,
                examinations=Examination(),  # Initialize with an instance of Examination
                sync_subject=False,
            )
        else:
            # Update the subject name if it is provided and different from the existing one
            if subject_code not in self.data_persistence.data[self.name]:
                self.data_persistence.data[self.name][subject_code] = OrderedDict(
                    [
                        ("Subject Name", subject_name if subject_name else "N/A"),
                        ("Assignments", []),
                        ("Total Mark", 0),
                        ("Examinations", {"Exam Mark": 0, "Exam Weight": 100}),
                    ]
                )

        return self.data_persistence.data[self.name][subject_code]

    def add_subject(self, subject_code: str, subject_name: str, sync_subject: bool = False):
        """
        Adds a new subject to the semester.
        This method validates the provided subject code and name, ensures the subject
        does not already exist, and then creates and adds a new Subject instance to the
        semester's subjects. The updated data is saved persistently.
        Args:
            subject_code (str): The unique code identifying the subject.
            subject_name (str): The name of the subject.
            sync_subject (bool, optional): Indicates whether the subject should be synchronized.
                                           Defaults to False.
        Returns:
            None: Displays a message box indicating success or failure.
        Raises:
            QMessageBox: Displays an error message if the subject code already exists or
                         if the subject code or name is empty.
        """

        if subject_code in self.subjects:
            QMessageBox.critical(None, "Error", f"Subject '{subject_code}' already exists.")
            return

        # Validate the subject code and name
        if not subject_code or not subject_name:
            QMessageBox.critical(None, "Error", "Subject code and name cannot be empty.")
            return

        # Create a new Subject instance
        subject = Subject(
            subject_code=subject_code,
            subject_name=subject_name,
            sync_subject=sync_subject,
        )

        # Add the subject to the semester's subjects
        self.subjects[subject_code] = subject

        # Save the updated data as serializable dictionaries
        self.data_persistence.data[self.name] = {code: subj for code, subj in self.subjects.items()}
        self.data_persistence.save_data(self.data_persistence.data)
        QMessageBox.information(None, "Info", f"Added new subject '{subject_name}' with code '{subject_code}'.")

    def delete_subject(self, subject_code: str):
        """
        Deletes a subject from the semester.

        Args:
            subject_code (str): The code of the subject to be deleted.

        Raises:
            ValueError: If the subject with the given code does not exist.

        Side Effects:
            - Removes the subject from the `subjects` dictionary.
            - Updates the persistent data storage to reflect the changes.
            - Saves the updated data to the persistence layer.
        """
        if subject_code not in self.subjects:
            raise ValueError(f"Subject '{subject_code}' does not exist.")
        del self.subjects[subject_code]
        self.data_persistence.data[self.name] = {code: subj.to_dict() for code, subj in self.subjects.items()}
        self.data_persistence.save_data(self.data_persistence.data)

    def add_entry(
        self,
        subject_code: str,
        subject_assessment: str,
        weighted_mark: Union[float, str],
        unweighted_mark: Optional[float],
        mark_weight: Optional[float],
        grade_type: Literal["numeric", "S", "U"],
    ) -> None:
        """
        Adds or updates an entry for a subject assessment in the semester.

        Parameters:
            subject_code (str): The code of the subject to which the assessment belongs.
            subject_assessment (str): The name or identifier of the assessment.
            weighted_mark (Union[float, str]): The weighted mark for the assessment.
                If the grade type is "S" or "U", this will be the grade itself.
            unweighted_mark (Optional[float]): The unweighted mark for the assessment.
                Calculated as weighted_mark divided by mark_weight if applicable.
            mark_weight (Optional[float]): The weight of the assessment mark.
                Used to calculate the unweighted mark.
            grade_type (Literal["numeric", "S", "U"]): The type of grade for the assessment.
                "numeric" indicates a numeric grade, "S" indicates satisfactory, and "U" indicates unsatisfactory.

        Returns:
            None

        Behavior:
            - If the subject code does not exist in the semester, an error message is displayed.
            - If the grade type is "S" or "U", unweighted_mark and mark_weight are set to None,
              and weighted_mark is set to the grade type.
            - If weighted_mark or mark_weight is None for numeric grades, an error message is displayed.
            - If the assessment already exists, its marks and weight are updated.
            - If the assessment does not exist, it is added to the subject's assignments.
            - Updates the persistent data storage and saves the changes.
            - Displays an informational message indicating whether the entry was added or updated.
        """
        if subject_code not in self.subjects:
            QMessageBox.critical(None, "Error", f"Subject '{subject_code}' does not exist in {self.name}.")
            return
        subject = self.subjects[subject_code]
        # Only assign float or None to unweighted_mark and mark_weight
        if grade_type in ("S", "U"):
            unweighted_mark = None
            mark_weight = None
            weighted_mark = grade_type  # "S" or "U"
        else:
            if weighted_mark is None or mark_weight is None:
                QMessageBox.critical(None, "Error", "Weighted mark and mark weight must not be empty.")
                return
            weighted_mark = float(weighted_mark)
            mark_weight = float(mark_weight)
            unweighted_mark = round(weighted_mark / mark_weight, 4) if mark_weight > 0 else 0

        updated = False
        for a in subject.assignments:
            if a.subject_assessment == subject_assessment:
                a.unweighted_mark = unweighted_mark
                a.weighted_mark = weighted_mark
                a.mark_weight = mark_weight
                updated = True
                break
        else:
            assignment = Assignment(
                subject_assessment=subject_assessment,
                unweighted_mark=unweighted_mark,
                weighted_mark=weighted_mark,
                mark_weight=mark_weight,
            )
            subject.assignments.append(assignment)

        self.data_persistence.data[self.name] = {code: subj.to_dict() for code, subj in self.subjects.items()}
        self.data_persistence.save_data(self.data_persistence.data)
        if updated:
            QMessageBox.information(
                None, "Info", f"Entry for '{subject_assessment}' updated in semester '{self.name}'."
            )
        else:
            QMessageBox.information(None, "Info", f"Entry for '{subject_assessment}' added in semester '{self.name}'.")

    def delete_entry(self, subject_code: str, subject_assessment: str):
        if subject_code in self.subjects:
            subject = self.subjects[subject_code]
            subject.assignments = [a for a in subject.assignments if a.subject_assessment != subject_assessment]
            self.data_persistence.data[self.name] = {code: subj.to_dict() for code, subj in self.subjects.items()}
            self.data_persistence.save_data(self.data_persistence.data)

    def calculate_exam_mark(self, subject_code: str) -> Optional[float]:
        """
        Calculate the exam mark for a given subject based on its assignments and examinations.
        Args:
            subject_code (str): The code of the subject for which the exam mark is to be calculated.
        Returns:
            Optional[float]: The calculated exam mark rounded to two decimal places, or None if the subject
            does not exist or the necessary data is unavailable.
        Notes:
            - If the subject has an `examinations` field with `exam_mark` and `exam_weight`, the exam mark
            is calculated as `exam_mark / exam_weight`.
            - If the subject does not have an `examinations` field or the necessary data is missing, the
            exam mark is calculated based on the weighted marks and weights of the assignments.
            - If neither method can provide a valid calculation, the function returns None.
        """

        subject = self.subjects.get(subject_code)
        if subject:
            # If you want to sum all assignment weighted marks and weights:
            total_weighted = sum(
                a.weighted_mark for a in subject.assignments if isinstance(a.weighted_mark, (float, int))
            )
            total_weight = sum(a.mark_weight for a in subject.assignments if a.mark_weight is not None)
            # If you want to use the exam mark from the examinations field:
            if hasattr(subject, "examinations") and subject.examinations is not None:
                exam_mark = getattr(subject.examinations, "exam_mark", None)
                exam_weight = getattr(subject.examinations, "exam_weight", None)
                if exam_mark is not None and exam_weight and exam_weight > 0:
                    return round(exam_mark / exam_weight, 2)
            # Or, if you want to calculate based on assignments:
            if total_weighted is not None and total_weight:
                return round(total_weighted / total_weight, 2)
        return None
