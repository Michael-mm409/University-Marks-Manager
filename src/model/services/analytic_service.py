"""Core analytics calculations and business logic."""

from typing import Dict, List, Optional, Tuple

from model import Assignment, Subject


class AnalyticsService:
    """
    AnalyticsService provides a collection of static methods to perform various analytical calculations related to assignments, exams, and grades.

    Methods:
        calculate_assignment_total(assignments: List[Assignment]) -> float: Calculate the total marks for a list of assignments, considering their weighted marks.
        calculate_weight_total(assignments: List[Assignment]) -> float: Calculate the total weight of a list of assignments.
        get_exam_mark(subject: Subject) -> Optional[float]: Retrieve the exam mark for a given subject, if available.
        detect_marking_scale(marks: List[float]) -> Tuple[float, float]: Detect the marking scale based on the provided marks and return the maximum mark and the scale factor.
        calculate_grade_distribution(marks: List[float], scale_factor: float = 1.0) -> Dict[str, int]: Calculate the grade distribution (HD, D, C, P, F) based on the provided marks and an optional scale factor.
        calculate_exam_requirements(subject: Subject) -> Dict[str, float]: Calculate the exam mark requirements for a subject based on the total mark and assignment marks, and determine if the required exam mark is achievable.
    """

    @staticmethod
    def calculate_assignment_total(assignments: List[Assignment]) -> float:
        """
        Calculates the total weighted marks for a list of assignments. This function iterates through a list of Assignment objects, checks if each assignment has a valid `weighted_mark`, and sums up the valid marks. If a `weighted_mark` is not valid (e.g., None, or cannot be converted to a float), it is ignored.

        Args:
            assignments (List[Assignment]): A list of Assignment objects, where each object may have a `weighted_mark` attribute.
        Returns:
            float: The total sum of valid weighted marks from the assignments.
        """

        total = 0.0
        for assignment in assignments:
            if assignment.weighted_mark is not None:
                try:
                    total += float(assignment.weighted_mark)
                except (TypeError, ValueError):
                    continue
        return total

    @staticmethod
    def calculate_weight_total(assignments: List[Assignment]) -> float:
        """
        Calculates the total weight of a list of assignments. This function iterates through a list of Assignment objects and sums up the `mark_weight` attribute of each assignment, provided it is not None and can be converted to a float. If a `mark_weight` is invalid (e.g., cannot be converted to a float), it is ignored.

        Args:
            assignments (List[Assignment]): A list of Assignment objects, each potentially containing a `mark_weight` attribute.
        Returns:
            float: The total weight of all valid `mark_weight` values in the assignments list.
        """

        total = 0.0
        for assignment in assignments:
            if assignment.mark_weight is not None:
                try:
                    total += float(assignment.mark_weight)
                except (TypeError, ValueError):
                    continue
        return total

    @staticmethod
    def get_exam_mark(subject: Subject) -> Optional[float]:
        """
        Retrieves the exam mark for a given subject if it exists.
        Args:
            subject (Subject): The subject object containing examination details.
        Returns:
            Optional[float]: The exam mark if it exists, otherwise None.
        """

        if hasattr(subject, "examinations") and subject.examinations:
            if hasattr(subject.examinations, "exam_mark"):
                return subject.examinations.exam_mark
        return None

    @staticmethod
    def detect_marking_scale(marks: List[float]) -> Tuple[float, float]:
        """
        Detects the marking scale based on the provided list of marks. This function determines the maximum mark in the list and returns a tuple containing the maximum mark and the corresponding scale factor. The scale
        factor is calculated as follows:
        - If the maximum mark is less than or equal to 20, the scale factor is `max_mark / 100`.
        - Otherwise, the scale factor is `1.0`. If the input list of marks is empty, the function defaults to a maximum mark of 100 and a scale factor of 1.0.

        Args:
            marks (List[float]): A list of numerical marks.
        Returns:
            Tuple[float, float]: A tuple containing:
                - The maximum mark (float).
                - The scale factor (float).
        """

        if not marks:
            return 100, 1.0

        max_mark = max(marks)
        if max_mark <= 20:
            return max_mark, max_mark / 100
        else:
            return max_mark, 1.0

    @staticmethod
    def calculate_grade_distribution(marks: List[float], scale_factor: float = 1.0) -> Dict[str, int]:
        """
        Calculates the grade distribution for a list of marks based on predefined grade boundaries.

        Args:
            marks (List[float]): A list of numerical marks to be analyzed.
            scale_factor (float, optional): A multiplier applied to the grade boundaries. Defaults to 1.0.

        Returns:
            Dict[str, int]: A dictionary containing the count of marks in each grade category:
                - "HD": High Distinction (marks >= 85 * scale_factor)
                - "D": Distinction (75 * scale_factor <= marks < 85 * scale_factor)
                - "C": Credit (65 * scale_factor <= marks < 75 * scale_factor)
                - "P": Pass (50 * scale_factor <= marks < 65 * scale_factor)
                - "F": Fail (marks < 50 * scale_factor)
        """

        return {
            "HD": len([m for m in marks if m >= (85 * scale_factor)]),
            "D": len([m for m in marks if (75 * scale_factor) <= m < (85 * scale_factor)]),
            "C": len([m for m in marks if (65 * scale_factor) <= m < (75 * scale_factor)]),
            "P": len([m for m in marks if (50 * scale_factor) <= m < (65 * scale_factor)]),
            "F": len([m for m in marks if m < (50 * scale_factor)]),
        }

    @staticmethod
    def calculate_exam_requirements(subject: Subject, ps_flag: bool = False) -> Dict[str, float]:
        """
        Calculate the exam requirements for a given subject.
        Normal scenario: required_exam = max(0, total_mark - assignment_total).
        Pass Supplementary (PS) scenario (ps_flag True and total_mark == 50):
            required_exam is proportional to the remaining weight share of the total mark:
                required_exam = (exam_weight / 100) * total_mark
            (Independent of assignment marks achieved; driven by assessment weighting.)
        Args:
            subject (Subject): The subject object containing details about
                assignments and the total mark required.
        Returns:
            Dict[str, float]: A dictionary containing:
                - "total_mark" (float): The total mark required for the subject.
                - "assignment_total" (float): The total marks obtained from assignments.
                - "required_exam" (float): The marks required in the exam to achieve the total mark.
                - "achievable" (bool): Whether the required exam mark is achievable (<= 100).
                - "exam_weight" (float): The weight of the exam (remaining weight after assignments).
        """

        if subject.total_mark is None:
            return {}

        assignment_total = AnalyticsService.calculate_assignment_total(subject.assignments)
        weight_total = AnalyticsService.calculate_weight_total(subject.assignments)
        exam_weight = max(0.0, 100 - weight_total)

        if ps_flag and subject.total_mark == 50:
            # PS rule: enforce user-specified minimum exam weight (default 40) and compute proportional requirement only.
            try:  # Access session_state lazily to avoid hard dependency if not in Streamlit context
                from streamlit import session_state as _st_session  # type: ignore

                min_exam_weight_key = f"ps_min_exam_weight_{subject.subject_code}"
                user_min_exam_weight = float(_st_session.get(min_exam_weight_key, 40.0))
            except Exception:
                user_min_exam_weight = 40.0
            # Clamp between 0 and 100
            enforced_min = max(0.0, min(100.0, user_min_exam_weight))
            exam_weight = enforced_min
            required_exam = (exam_weight / 100.0) * subject.total_mark
        else:
            required_exam = max(0.0, subject.total_mark - assignment_total)

        return {
            "total_mark": subject.total_mark,
            "assignment_total": assignment_total,
            "required_exam": required_exam,
            "achievable": required_exam <= 100,
            "exam_weight": exam_weight,
        }
