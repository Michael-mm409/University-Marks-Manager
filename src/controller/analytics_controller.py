"""Controller for analytics operations."""

from typing import Any, Dict, Optional

from model.domain.entities.subject import Subject
from model.services.analytic_service import AnalyticsService
from model.services.grade_calc_service import GradeCalculationService
from model.services.performance_metrics_service import PerformanceMetricsService


class AnalyticsController:
    """
    AnalyticsController manages and provides analytics for subjects, including metrics,
    grade status, assignment analytics, performance trends, and exam insights.

    Args:
        app_controller (AppController): Manages the semester object.
        analytics_service (AnalyticsService): Handles analytics-related calculations.
        grade_service (GradeCalculationService): Handles grade-related calculations.
        metrics_service (PerformanceMetricsService): Handles performance metrics calculations.

    Methods:
        get_subject_analytics(subject_code: str) -> Optional[Dict[str, Any]]:
            Provides comprehensive analytics for a subject.
        _get_basic_metrics(subject: Subject) -> Dict[str, Any]:
            Computes basic metrics like total marks, assignment totals, and remaining weight.
        _get_grade_status(subject: Subject) -> Dict[str, Any]:
            Provides grade status, including grade value, level, and progress percentage.
        _get_assignment_analytics(subject: Subject) -> Dict[str, Any]:
            Analyzes assignments, including marks, grade distribution, and performance metrics.
        _calculate_grade_distribution_from_assignments(assignment_data) -> Dict[str, int]:
            Computes grade distribution using assignment marks and weights.
        _get_performance_analytics(subject: Subject) -> Dict[str, Any]:
            Analyzes performance trends and progress to targets.
        _get_exam_analytics(subject: Subject) -> Dict[str, Any]:
            Provides exam-related analytics, including marks and requirements.
    """

    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.analytics_service = AnalyticsService()
        self.grade_service = GradeCalculationService()
        self.metrics_service = PerformanceMetricsService()

    def get_subject_analytics(self, subject_code: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves analytics data for a specific subject based on the provided subject code.
        Args:
            subject_code (str): The code of the subject for which analytics are to be retrieved.
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the following analytics data for the subject:
                - "subject_code" (str): The code of the subject.
                - "basic_metrics" (Any): Basic metrics related to the subject.
                - "grade_status" (Any): Grade status information for the subject.
                - "assignment_analytics" (Any): Analytics related to assignments in the subject.
                - "performance_analytics" (Any): Performance analytics for the subject.
                - "exam_analytics" (Any): Exam-related analytics for the subject.
              Returns None if the semester object or the subject is not found.
        """
        if not self.app_controller.semester_obj:
            return None

        subject = self.app_controller.semester_obj.subjects.get(subject_code)
        if not subject:
            return None

        return {
            "subject_code": subject_code,
            "basic_metrics": self._get_basic_metrics(subject),
            "grade_status": self._get_grade_status(subject),
            "assignment_analytics": self._get_assignment_analytics(subject),
            "performance_analytics": self._get_performance_analytics(subject),
            "exam_analytics": self._get_exam_analytics(subject),
        }

    def _get_basic_metrics(self, subject: Subject) -> Dict[str, Any]:
        """Calculate and return basic metrics for a given subject.

        Args:
            subject (Subject): The subject for which metrics are calculated.

        Returns:
            Dict[str, Any]: A dictionary containing basic metrics such as total marks,
            assignment totals, exam marks, weight totals, remaining weight, and assignment count.
        """
        assignment_total = self.analytics_service.calculate_assignment_total(subject.assignments)
        exam_mark = self.analytics_service.get_exam_mark(subject)
        weight_total = self.analytics_service.calculate_weight_total(subject.assignments)

        return {
            "total_mark": subject.total_mark,
            "assignment_total": assignment_total,
            "exam_mark": exam_mark,
            "weight_total": weight_total,
            "remaining_weight": 100 - weight_total,
            "assignment_count": len([a for a in subject.assignments if a.weighted_mark is not None]),
        }

    def _get_grade_status(self, subject: Subject) -> Dict[str, Any]:
        """
        Calculate and return the grade status for a given subject.

        Args:
            subject (Subject): The subject for which the grade status is to be calculated.

        Returns:
            Dict[str, Any]: A dictionary containing:
            - "grade_value" (float): Calculated grade value.
            - "grade_source" (str): Source of the grade (e.g., calculated or manual).
            - "has_total_mark" (bool): Whether the subject has a total mark.
            - "grade_level" (str): Grade level (e.g., "High Distinction").
            - "emoji" (str): Emoji representation of the grade level.
            - "progress_percent" (float): Progress percentage, capped at 1.0.
        """
        grade_value, grade_source, has_total_mark = self.grade_service.calculate_grade_status(subject)
        grade_level, emoji = self.grade_service.get_grade_level(grade_value)

        return {
            "grade_value": grade_value,
            "grade_source": grade_source,
            "has_total_mark": has_total_mark,
            "grade_level": grade_level,
            "emoji": emoji,
            "progress_percent": min(grade_value / 100, 1.0) if grade_value > 0 else 0,
        }

    def _get_assignment_analytics(self, subject: Subject) -> Dict[str, Any]:
        """
        Analyzes assignment data for a given subject and computes various analytics.

        Args:
            subject (Subject): The subject containing assignment data to analyze.

        Returns:
            Dict[str, Any]: A dictionary containing the following keys:
                - "has_data" (bool): Indicates whether valid assignment data exists.
                - "assignment_data" (List[Dict[str, Any]]): A list of dictionaries, each containing:
                    - "name" (str): The name of the assignment.
                    - "mark" (float): The weighted mark of the assignment.
                    - "weight" (float): The weight of the assignment.
                    - "max_mark" (float): The maximum mark for the assignment.
                - "marks" (List[float]): A list of weighted marks for all assignments.
                - "max_mark" (float): The maximum mark detected across all assignments.
                - "scale_factor" (float): The scale factor for normalizing marks.
                - "is_small_scale" (bool): Indicates if the maximum mark is less than or equal to 20.
                - "grade_distribution" (Dict[str, int]): The grade distribution calculated from assignment data.
                - "performance_metrics" (Dict[str, Any]): Performance metrics calculated from assignment marks.
        Raises:
            TypeError: If assignment marks cannot be converted to float.
            ValueError: If invalid values are encountered during processing.
        """

        assignment_marks = []
        assignment_data = []

        for assignment in subject.assignments:
            if assignment.weighted_mark is not None:
                try:
                    mark = float(assignment.weighted_mark)
                    weight = float(assignment.mark_weight) if assignment.mark_weight else 0.0

                    assignment_marks.append(mark)
                    assignment_data.append(
                        {
                            "name": assignment.subject_assessment,
                            "mark": mark,
                            "weight": weight,
                            "max_mark": weight,  # Add max_mark for grade calculation
                        }
                    )
                except (TypeError, ValueError):
                    continue

        if not assignment_marks:
            return {"has_data": False}

        max_mark, scale_factor = self.analytics_service.detect_marking_scale(assignment_marks)

        # FIX: Calculate grade distribution using individual assignment data instead of just marks
        grade_distribution = self._calculate_grade_distribution_from_assignments(assignment_data)

        performance_metrics = self.metrics_service.calculate_performance_metrics(assignment_marks)

        return {
            "has_data": True,
            "assignment_data": assignment_data,
            "marks": assignment_marks,
            "max_mark": max_mark,
            "scale_factor": scale_factor,
            "is_small_scale": max_mark <= 20,
            "grade_distribution": grade_distribution,
            "performance_metrics": performance_metrics,
        }

    def _calculate_grade_distribution_from_assignments(self, assignment_data) -> Dict[str, int]:
        """
        Calculates the grade distribution from a list of assignment data.
        This method takes a list of assignments, each containing a mark and a maximum weight,
        and calculates the distribution of grades (HD, D, C, P, F) based on the percentage
        of marks obtained.
        Args:
            assignment_data (List[Dict[str, Union[int, float]]]): A list of dictionaries where each dictionary
            represents an assignment with the following keys:
            - "mark" (int or float): The mark obtained for the assignment.
            - "weight" (int or float): The maximum possible mark for the assignment.
        Returns:
            Dict[str, int]: A dictionary containing the count of assignments in each grade category:
            - "HD": High Distinction (percentage >= 85)
            - "D": Distinction (75 <= percentage < 85)
            - "C": Credit (65 <= percentage < 75)
            - "P": Pass (50 <= percentage < 65)
            - "F": Fail (percentage < 50)
        """

        grade_counts = {"HD": 0, "D": 0, "C": 0, "P": 0, "F": 0}

        for assignment in assignment_data:
            mark = assignment["mark"]
            max_mark = assignment["weight"]  # weight is the maximum mark

            if max_mark > 0:
                percentage = (mark / max_mark) * 100

                if percentage >= 85:
                    grade_counts["HD"] += 1
                elif percentage >= 75:
                    grade_counts["D"] += 1
                elif percentage >= 65:
                    grade_counts["C"] += 1
                elif percentage >= 50:
                    grade_counts["P"] += 1
                else:
                    grade_counts["F"] += 1

        return grade_counts

    def _get_performance_analytics(self, subject: Subject) -> Dict[str, Any]:
        """
        Computes performance analytics for a given subject.
        Args:
            subject (Subject): The subject for which performance analytics are to be calculated.
        Returns:
            Dict[str, Any]: A dictionary containing the following keys:
                - "has_total_mark" (bool): Indicates whether the subject has a valid total mark.
                - "progress_to_targets" (Any, optional): The progress towards targets based on the subject's total mark.
                  Only included if "has_total_mark" is True.
                - "trend_analysis" (Any): The trend analysis of assignment marks for the subject.
        """

        analytics: Dict[str, Any] = {"has_total_mark": subject.total_mark is not None and subject.total_mark >= 0}

        if analytics["has_total_mark"]:
            analytics["progress_to_targets"] = self.metrics_service.calculate_progress_to_targets(subject.total_mark)

        # Trend analysis for assignments
        assignment_marks = []
        for assignment in subject.assignments:
            if assignment.weighted_mark is not None:
                try:
                    assignment_marks.append(float(assignment.weighted_mark))
                except (TypeError, ValueError):
                    continue

        analytics["trend_analysis"] = self.metrics_service.analyze_trend(assignment_marks)
        return analytics

    def _get_exam_analytics(self, subject: Subject) -> Dict[str, Any]:
        """
        Computes and returns analytics related to the exam for a given subject.

        Args:
            subject (Subject): The subject for which exam analytics are to be calculated.

        Returns:
            Dict[str, Any]: A dictionary containing the following keys:
                - "has_exam" (bool): Indicates whether the subject has an exam.
                - "exam_mark" (Optional[float]): The exam mark for the subject, if available.
                - "requirements" (Optional[Dict[str, Any]]): The calculated exam requirements, if the total mark is available.
                - "needs_update" (Optional[bool]): Indicates whether the exam mark needs to be updated, based on a threshold difference.
                - "calculated_exam" (Optional[float]): The calculated required exam mark, if applicable.
        """

        exam_mark = self.analytics_service.get_exam_mark(subject)
        has_exam = exam_mark is not None

        analytics: Dict[str, Any] = {"has_exam": has_exam, "exam_mark": exam_mark}

        if subject.total_mark is not None:
            exam_requirements = self.analytics_service.calculate_exam_requirements(subject)
            analytics["requirements"] = exam_requirements

            if has_exam and exam_requirements:
                difference = abs(exam_requirements["required_exam"] - exam_mark)
                analytics["needs_update"] = difference > 0.1
                analytics["calculated_exam"] = exam_requirements["required_exam"]

        return analytics
