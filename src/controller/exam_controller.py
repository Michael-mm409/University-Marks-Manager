"""Controller for exam operations."""

from model.domain.entities.examination import Examination
from model.services.analytic_service import AnalyticsService


class ExamController:
    """Controller for exam-related operations."""

    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.analytics_service = AnalyticsService()

    def auto_calculate_exam(self, subject_code: str) -> bool:
        """Auto-calculate and save exam mark."""
        try:
            if not self.app_controller.semester_obj:
                return False

            subject = self.app_controller.semester_obj.subjects.get(subject_code)
            if not subject or subject.total_mark is None:
                return False

            exam_requirements = self.analytics_service.calculate_exam_requirements(subject)
            weight_total = self.analytics_service.calculate_weight_total(subject.assignments)
            remaining_weight = 100 - weight_total

            subject.examinations = Examination(
                exam_mark=exam_requirements["required_exam"], exam_weight=remaining_weight
            )

            self.app_controller.semester_obj.data_persistence.save_data(
                self.app_controller.semester_obj.data_persistence.data
            )

            return True

        except Exception:
            return False

    def update_exam_manually(self, subject_code: str, exam_mark: float, exam_weight: float) -> bool:
        """Update exam mark manually."""
        try:
            if not self.app_controller.semester_obj:
                return False

            subject = self.app_controller.semester_obj.subjects.get(subject_code)
            if not subject:
                return False

            subject.examinations = Examination(exam_mark=exam_mark, exam_weight=exam_weight)

            self.app_controller.semester_obj.data_persistence.save_data(
                self.app_controller.semester_obj.data_persistence.data
            )

            return True

        except Exception:
            return False
