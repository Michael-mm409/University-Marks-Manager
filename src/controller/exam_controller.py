"""Controller for exam operations."""

from model.domain.entities.examination import Examination
from model.services.analytic_service import AnalyticsService


class ExamController:
    """
    A controller class responsible for managing examination-related operations
    within the application.

    Methods
        __init__(app_controller)
            Initializes the ExamController with a reference to the main application
            controller and sets up the analytics service.
        auto_calculate_exam(subject_code: str) -> bool
            Automatically calculates and saves the required exam mark for a given
            subject based on its current assignments and total mark.
        update_exam_manually(subject_code: str, exam_mark: float, exam_weight: float) -> bool
            Manually updates the exam mark and weight for a given subject.
    """

    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.analytics_service = AnalyticsService()

    def auto_calculate_exam(self, subject_code: str) -> bool:
        """
        Automatically calculates the required exam mark and updates the subject's examination details.
        This method calculates the required exam mark for a given subject based on its current assignments
        and their weights. It then updates the subject's examination details with the calculated exam mark
        and the remaining weight. The updated data is persisted to storage.

        Args:
            subject_code (str): The code of the subject for which the exam mark is to be calculated.

        Returns:
            bool: True if the calculation and update were successful, False otherwise.

        Raises:
            Exception: If any unexpected error occurs during the calculation or update process.
        """

        try:
            if not self.app_controller.semester_obj:
                return False

            subject = self.app_controller.semester_obj.subjects.get(subject_code)
            if not subject or subject.total_mark is None:
                return False

            # Assignment weights used implicitly via analytics service; explicit aggregation not needed here

            # Pass Supplementary logic: explicit flag takes precedence; fallback to total_mark heuristic
            from streamlit import session_state as _st_session

            ps_flag_key = f"ps_flag_{subject_code}"
            is_ps = bool(_st_session.get(ps_flag_key, False))
            if not is_ps and subject.total_mark == 50:
                # Heuristic fallback only if user hasn't explicitly toggled
                is_ps = True
            # Delegate calculation (PS or normal) to analytics service
            exam_requirements = self.analytics_service.calculate_exam_requirements(subject, ps_flag=is_ps)
            exam_mark = exam_requirements.get("required_exam", 0.0)
            exam_weight = exam_requirements.get("exam_weight", 0.0)

            subject.examinations = Examination(exam_mark=exam_mark, exam_weight=exam_weight)
            persistence = self.app_controller.semester_obj.data_persistence
            if hasattr(persistence, "upsert_exam"):
                persistence.upsert_exam(self.app_controller.semester_obj.name, subject_code, exam_mark, exam_weight)  # type: ignore[attr-defined]
            else:  # legacy fallback
                persistence.save_data(persistence.data)  # type: ignore[attr-defined]

            return True

        except Exception:
            return False

    def update_exam_manually(self, subject_code: str, exam_mark: float, exam_weight: float) -> bool:
        """
        Updates the examination details for a specific subject manually.
        This method allows the user to update the examination mark and weight for a
        given subject code. The updated data is persisted to storage.
        Args:
            subject_code (str): The code of the subject to update.
            exam_mark (float): The mark obtained in the examination.
            exam_weight (float): The weight of the examination in the subject's overall assessment.
        Returns:
            bool: True if the update was successful, False otherwise.
        Raises:
            Exception: If an unexpected error occurs during the update process.
        """

        try:
            if not self.app_controller.semester_obj:
                return False

            subject = self.app_controller.semester_obj.subjects.get(subject_code)
            if not subject:
                return False

            subject.examinations = Examination(exam_mark=exam_mark, exam_weight=exam_weight)
            persistence = self.app_controller.semester_obj.data_persistence
            if hasattr(persistence, "upsert_exam"):
                persistence.upsert_exam(self.app_controller.semester_obj.name, subject_code, exam_mark, exam_weight)  # type: ignore[attr-defined]
            else:
                persistence.save_data(persistence.data)  # type: ignore[attr-defined]

            return True

        except Exception:
            return False
