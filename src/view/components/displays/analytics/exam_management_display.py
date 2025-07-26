"""Exam management display components.

This module provides a comprehensive exam management interface for the University
Marks Manager, handling exam mark entry, updates, and intelligent calculations.
It offers both manual entry and automatic calculation capabilities based on
assignment performance and target grades.

Key Features:
    - Exam mark entry and modification with validation
    - Automatic exam calculation based on assignment performance
    - Exam requirements calculator with target grade analysis
    - Interactive advice system for exam preparation
    - Update detection for calculated vs. recorded exam marks

The module integrates with the ExamController to handle data persistence and
calculation logic while providing a user-friendly Streamlit interface.

Example:
    >>> from controller.app_controller import AppController
    >>> controller = AppController()
    >>> exam_display = ExamManagementDisplay(controller)
    >>> exam_display.render(analytics_data)
"""

from typing import Any, Dict, Optional

import streamlit as st

from controller import AppController, ExamController


class ExamManagementDisplay:
    """Handles exam management display and user interactions.

    This class provides a complete exam management interface, including exam
    mark entry, updates, calculations, and advice. It manages both manual entry
    workflows and automatic calculation features based on assignment performance.

    The class handles multiple exam states:
        - No exam recorded: Provides entry form with suggestions
        - Exam exists: Shows current mark with update options
        - Update available: Notifies when calculated mark differs from recorded
        - Calculation helper: Provides exam requirements analysis

    Attributes:
        controller: Main application controller for data access
        exam_controller: Specialized controller for exam operations

    Design Principles:
        - Progressive disclosure: Shows relevant options based on current state
        - Intelligent defaults: Pre-fills forms with calculated suggestions
        - Clear feedback: Provides immediate success/error messages
        - Helpful guidance: Offers advice based on exam requirements

    Example:
        >>> controller = AppController()
        >>> display = ExamManagementDisplay(controller)
        >>> display.render(analytics_data)
    """

    def __init__(self, controller: AppController) -> None:
        """Initialize exam management display with controllers.

        Args:
            controller: Main application controller providing data access
        """
        self.controller: AppController = controller
        self.exam_controller: ExamController = ExamController(controller)

    def render(self, analytics_data: Dict[str, Any]) -> None:
        """Render exam management section with state-based interface.

        Provides different interfaces based on whether an exam is already recorded.
        Handles the main routing logic to appropriate sub-interfaces.

        Args:
            analytics_data: Complete analytics dataset containing:
                - exam_analytics: Exam-specific data and calculations
                - subject_code: Subject identifier for operations

        Interface States:
            - Existing exam: Shows current mark with update options
            - No exam: Provides entry form with automatic calculation options

        Example:
            >>> display.render(analytics_data)
        """
        st.subheader("📝 Exam Management")

        exam_analytics: Dict[str, Any] = analytics_data["exam_analytics"]
        subject_code: str = analytics_data["subject_code"]

        if exam_analytics["has_exam"]:
            self._render_existing_exam(exam_analytics, subject_code)
        else:
            self._render_add_exam_form(exam_analytics, subject_code)

    def _render_existing_exam(self, exam_analytics: Dict[str, Any], subject_code: str) -> None:
        """Render existing exam management with update options.

        Displays current exam information and provides options for updating
        when calculated marks differ from recorded marks. Includes both
        automatic update and manual update capabilities.

        Args:
            exam_analytics: Exam data containing current mark and calculations
            subject_code: Subject identifier for update operations

        Features:
            - Current exam mark display with success styling
            - Update detection with warning when marks differ
            - One-click auto-update to calculated mark
            - Manual update form in expandable section

        Update Logic:
            - Compares recorded mark with calculated mark
            - Shows warning when differences are detected
            - Provides quick update button for calculated mark
            - Offers manual override in collapsible form

        Example:
            >>> self._render_existing_exam(exam_analytics, "CSCI251")
        """
        exam_mark: float = exam_analytics["exam_mark"]
        st.success(f"✅ **Exam recorded:** {exam_mark:.1f}")

        # Check for updates needed
        if exam_analytics.get("needs_update", False):
            calculated: float = exam_analytics["calculated_exam"]
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

    def _render_add_exam_form(self, exam_analytics: Dict[str, Any], subject_code: str) -> None:
        """Render exam entry form for new exam records.

        Provides interface for adding new exam marks with intelligent suggestions
        based on assignment performance and target grades. Offers both automatic
        calculation and manual entry options.

        Args:
            exam_analytics: Exam analytics containing calculation suggestions
            subject_code: Subject identifier for save operations

        Features:
            - Automatic exam calculation based on assignment performance
            - Suggested exam mark display with explanation
            - One-click auto-calculate and save functionality
            - Manual entry form for custom marks

        Workflow:
            1. Display information about missing exam
            2. Show calculated suggestion if requirements available
            3. Provide auto-calculate button for quick entry
            4. Offer manual form for custom values

        Example:
            >>> self._render_add_exam_form(exam_analytics, "CSCI251")
        """
        st.info("📝 **No exam recorded.** Add your exam mark below:")

        # Auto-calculate option
        if "requirements" in exam_analytics:
            requirements: Dict[str, Any] = exam_analytics["requirements"]
            suggested_exam: float = requirements["required_exam"]

            st.info(f"🎯 **Suggested exam mark:** {suggested_exam:.1f}")

            if st.button("🎮 Auto-Calculate & Save Exam", key=f"auto_calc_{subject_code}"):
                if self.exam_controller.auto_calculate_exam(subject_code):
                    st.success("✅ Auto-calculated exam saved!")
                    st.rerun()
                else:
                    st.error("Error saving exam")

        # Manual entry form
        self._render_exam_form(exam_analytics, subject_code, "Add")

    def _render_exam_form(self, exam_analytics: Dict[str, Any], subject_code: str, action: str) -> None:
        """Render exam input form with intelligent defaults and validation.

        Creates a form for exam mark and weight entry with smart default values
        based on current context (add vs. update) and available calculations.

        Args:
            exam_analytics: Exam data containing suggestions and current values
            subject_code: Subject identifier for form operations
            action: Form action type ("Add" or "Update")

        Form Features:
            - Two-column layout for mark and weight input
            - Intelligent default value calculation
            - Input validation with min/max constraints
            - Helpful tooltips and guidance
            - Error handling for invalid data types

        Default Value Logic:
            - Add: Uses calculated suggestion or 0.0
            - Update: Uses current exam mark or calculated value
            - Weight: Defaults to 50% with user override capability

        Validation:
            - Exam mark: 0.0 to 100.0 range
            - Exam weight: 0.0 to 100.0 percentage
            - Type safety: Handles string/None conversions

        Example:
            >>> self._render_exam_form(exam_analytics, "CSCI251", "Add")
        """
        with st.form(f"exam_form_{subject_code}_{action.lower()}"):
            exam_mark_column, exam_weight_column = st.columns(2)

            # Set default values, ensuring they are floats
            suggested_exam: float = 0.0
            suggested_weight: float = 50.0

            # Get suggested exam mark if available
            if "requirements" in exam_analytics and exam_analytics["requirements"]:
                requirements: Dict[str, Any] = exam_analytics["requirements"]
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

            with exam_mark_column:
                exam_mark: float = st.number_input(
                    "Exam Mark",
                    min_value=0.0,
                    max_value=100.0,
                    value=suggested_exam,
                    step=0.1,
                    help="Enter your exam mark (0-100)",
                )

            with exam_weight_column:
                exam_weight: float = st.number_input(
                    "Exam Weight (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=suggested_weight,
                    step=1.0,
                    help="Enter the exam weight percentage",
                )

            if st.form_submit_button(f"🎮 {action} Exam Manually", type="primary"):
                if self.exam_controller.update_exam_manually(subject_code, exam_mark, exam_weight):
                    st.success(f"✅ Exam {action.lower()}ed manually!")
                    st.rerun()
                else:
                    st.error(f"Error {action.lower()}ing exam")

        # Exam calculator helper
        if "requirements" in exam_analytics and exam_analytics["requirements"]:
            self._render_exam_calculator(exam_analytics)

    def _render_exam_calculator(self, exam_analytics: Dict[str, Any]) -> None:
        """Render exam requirements calculator with detailed breakdown.

        Provides a comprehensive exam calculation helper showing the relationship
        between total marks, assignment performance, and exam requirements.
        Includes formula explanation and study advice.

        Args:
            exam_analytics: Exam analytics containing calculation requirements

        Calculator Features:
            - Total mark, assignment total, and required exam display
            - Formula breakdown showing calculation logic
            - Color-coded metrics for easy interpretation
            - Study advice based on required exam performance

        Data Safety:
            - Handles None/invalid values gracefully
            - Provides error messages for calculation failures
            - Uses default values for missing data

        Advice Categories:
            - Already achieved target (≤0 required)
            - Very achievable (≤50 required)
            - Study well (≤70 required)
            - Challenging (≤85 required)
            - Very challenging (≤100 required)
            - Not achievable (>100 required)

        Example:
            >>> self._render_exam_calculator(exam_analytics)
        """
        # with st.expander("🎮 Exam Calculator"):
        st.markdown("**Quick calculation to help you plan:**")

        requirements: Dict[str, Any] = exam_analytics["requirements"]

        # Safely extract values with defaults
        total_mark: Optional[float] = requirements.get("total_mark", 0.0)
        assignment_total: Optional[float] = requirements.get("assignment_total", 0.0)
        required_exam: Optional[float] = requirements.get("required_exam", 0.0)

        # Ensure all values are valid numbers
        try:
            total_mark = float(total_mark) if total_mark is not None else 0.0
            assignment_total = float(assignment_total) if assignment_total is not None else 0.0
            required_exam = float(required_exam) if required_exam is not None else 0.0
        except (TypeError, ValueError):
            st.error("⚠️ Unable to calculate exam requirements due to invalid data.")
            return

        total_mark_column, assignment_total_column, needed_exam_column = st.columns(3)
        with total_mark_column:
            st.metric("Total Mark", f"{total_mark:.1f}")
        with assignment_total_column:
            st.metric("Assignment Total", f"{assignment_total:.1f}")
        with needed_exam_column:
            st.metric("Required Exam", f"{required_exam:.1f}")

        # Show calculation formula
        st.info(
            f"**Formula:** {total_mark:.1f} (Total) - {assignment_total:.1f} (Assignments) = {required_exam:.1f} (Exam)"
        )

        # Simple advice
        self._render_exam_advice(required_exam)

    def _render_exam_advice(self, required_exam: float) -> None:
        """Render personalized exam advice based on required performance.

        Provides encouraging and realistic advice based on the calculated
        exam mark requirements. Uses color-coded messages to convey
        the difficulty level and appropriate study recommendations.

        Args:
            required_exam: Calculated exam mark needed to achieve target

        Advice Categories:
            - Already achieved (≤0): Congratulatory message
            - Very achievable (≤50): Encouraging, standard preparation
            - Study well (≤70): Motivational, increased study emphasis
            - Challenging (≤85): Realistic warning, intensive preparation
            - Very challenging (≤100): Serious warning, maximum effort
            - Not achievable (>100): Honest assessment, alternative suggestions

        Message Styling:
            - Success: Green for achievable targets
            - Info: Blue for moderate requirements
            - Warning: Yellow for challenging targets
            - Error: Red for very difficult/impossible targets

        Example:
            >>> self._render_exam_advice(65.5)  # Shows "study well" advice
        """
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
                (f"❌ You need {required_exam:.1f} marks on the exam - this exceeds 100% and may not be achievable.")
            )
