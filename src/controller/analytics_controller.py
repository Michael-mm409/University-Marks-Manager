"""Controller for analytics operations."""

from typing import Any, Dict, Optional

from model.domain.entities.subject import Subject
from model.services.analytic_service import AnalyticsService
from model.services.grade_calc_service import GradeCalculationService
from model.services.performance_metrics_service import PerformanceMetricsService


class AnalyticsController:
    """Controller for analytics-related operations."""

    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.analytics_service = AnalyticsService()
        self.grade_service = GradeCalculationService()
        self.metrics_service = PerformanceMetricsService()

    def get_subject_analytics(self, subject_code: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive analytics for a subject."""
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
        """Get basic subject metrics."""
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
        """Get grade status information."""
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
        """Get assignment analytics."""
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
        """Calculate grade distribution using individual assignment max marks."""
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
        """Get performance analytics."""
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
        """Get exam analytics."""
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
