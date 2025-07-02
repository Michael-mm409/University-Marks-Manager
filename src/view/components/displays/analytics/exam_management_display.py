"""Exam management display components."""

import streamlit as st

from controller.app_controller import AppController
from controller.exam_controller import ExamController


class ExamManagementDisplay:
    """Handles exam management display."""

    def __init__(self, controller: AppController):
        self.controller = controller
        self.exam_controller = ExamController(controller)

    def render(self, analytics_data: dict) -> None:
        """Render exam management section."""
        st.subheader("📝 Exam Management")

        exam_analytics = analytics_data["exam_analytics"]
        subject_code = analytics_data["subject_code"]

        if exam_analytics["has_exam"]:
            self._render_existing_exam(exam_analytics, subject_code)
        else:
            self._render_add_exam_form(exam_analytics, subject_code)

    def _render_existing_exam(self, exam_analytics: dict, subject_code: str) -> None:
        """Render existing exam management."""
        exam_mark = exam_analytics["exam_mark"]
        st.success(f"✅ **Exam recorded:** {exam_mark:.1f}")

        # Check for updates needed
        if exam_analytics.get("needs_update", False):
            calculated = exam_analytics["calculated_exam"]
            st.warning(f"⚠️ **Update Available:** Calculated exam mark is {calculated:.1f}")

            if st.button("🔄 Auto-Update to Calculated Mark", key=f"auto_update_{subject_code}"):
                if self.exam_controller.auto_calculate_exam(subject_code):
                    st.success("✅ Auto-updated exam mark")
                    st.rerun()
                else:
                    st.error("Error updating exam")

        # Manual update option
        with st.expander("🔄 Manual Update"):
            self._render_exam_form(exam_analytics, subject_code, "Update")

    def _render_add_exam_form(self, exam_analytics: dict, subject_code: str) -> None:
        """Render add exam form."""
        st.info("📝 **No exam recorded.** Add your exam mark below:")

        # Auto-calculate option
        if "requirements" in exam_analytics:
            requirements = exam_analytics["requirements"]
            suggested_exam = requirements["required_exam"]

            st.info(f"💡 **Suggested exam mark:** {suggested_exam:.1f}")

            if st.button("🎯 Auto-Calculate & Save Exam", key=f"auto_calc_{subject_code}"):
                if self.exam_controller.auto_calculate_exam(subject_code):
                    st.success("✅ Auto-calculated exam saved!")
                    st.rerun()
                else:
                    st.error("Error saving exam")

        # Manual entry form
        self._render_exam_form(exam_analytics, subject_code, "Add")

    def _render_exam_form(self, exam_analytics: dict, subject_code: str, action: str) -> None:
        """Render exam input form."""
        with st.form(f"exam_form_{subject_code}_{action.lower()}"):
            col1, col2 = st.columns(2)

            # Set default values, ensuring they are floats
            suggested_exam = 0.0
            suggested_weight = 50.0

            # Get suggested exam mark if available
            if "requirements" in exam_analytics and exam_analytics["requirements"]:
                requirements = exam_analytics["requirements"]
                if "required_exam" in requirements and requirements["required_exam"] is not None:
                    try:
                        suggested_exam = float(requirements["required_exam"])
                    except (TypeError, ValueError):
                        suggested_exam = 0.0

            # For updates, use current exam mark if available
            if action == "Update" and exam_analytics.get("exam_mark") is not None:
                try:
                    suggested_exam = float(exam_analytics["exam_mark"])
                except (TypeError, ValueError):
                    suggested_exam = 0.0

            with col1:
                exam_mark = st.number_input(
                    "Exam Mark",
                    min_value=0.0,
                    max_value=100.0,
                    value=suggested_exam,
                    step=0.1,
                    help="Enter your exam mark (0-100)",
                )

            with col2:
                exam_weight = st.number_input(
                    "Exam Weight (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=suggested_weight,
                    step=1.0,
                    help="Enter the exam weight percentage",
                )

            if st.form_submit_button(f"🎯 {action} Exam Manually", type="primary"):
                if self.exam_controller.update_exam_manually(subject_code, exam_mark, exam_weight):
                    st.success(f"✅ Exam {action.lower()}ed manually!")
                    st.rerun()
                else:
                    st.error(f"Error {action.lower()}ing exam")

        # Exam calculator helper
        if "requirements" in exam_analytics and exam_analytics["requirements"]:
            self._render_exam_calculator(exam_analytics)

    def _render_exam_calculator(self, exam_analytics: dict) -> None:
        """Render exam calculator helper."""
        with st.expander("🧮 Exam Calculator"):
            st.markdown("**Quick calculation to help you plan:**")

            requirements = exam_analytics["requirements"]

            # Safely extract values with defaults
            total_mark = requirements.get("total_mark", 0.0)
            assignment_total = requirements.get("assignment_total", 0.0)
            required_exam = requirements.get("required_exam", 0.0)

            # Ensure all values are valid numbers
            try:
                total_mark = float(total_mark) if total_mark is not None else 0.0
                assignment_total = float(assignment_total) if assignment_total is not None else 0.0
                required_exam = float(required_exam) if required_exam is not None else 0.0
            except (TypeError, ValueError):
                st.error("⚠️ Unable to calculate exam requirements due to invalid data.")
                return

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Mark", f"{total_mark:.1f}")
            with col2:
                st.metric("Assignment Total", f"{assignment_total:.1f}")
            with col3:
                st.metric("Required Exam", f"{required_exam:.1f}")

            # Show calculation formula
            st.info(
                f"**Formula:** {total_mark:.1f} (Total) - {assignment_total:.1f} (Assignments) = {required_exam:.1f} (Exam)"
            )

            # Simple advice
            self._render_exam_advice(required_exam)

    def _render_exam_advice(self, required_exam: float) -> None:
        """Render exam advice based on required exam mark."""
        if required_exam <= 0:
            st.success("🎉 You've already achieved your target with assignments!")
        elif required_exam <= 50:
            st.success(f"✅ You need {required_exam:.1f} marks on the exam - very achievable!")
        elif required_exam <= 70:
            st.info(f"📚 You need {required_exam:.1f} marks on the exam - study well!")
        elif required_exam <= 85:
            st.warning(f"⚠️ You need {required_exam:.1f} marks on the exam - challenging but possible!")
        elif required_exam <= 100:
            st.error(f"🔥 You need {required_exam:.1f} marks on the exam - this will be very challenging!")
        else:
            st.error(
                f"❌ You need {required_exam:.1f} marks on the exam - this exceeds 100% and may not be achievable."
            )
