"""Fixed NavigationBar that doesn't hang."""

import streamlit as st

from controller.app_controller import AppController


class NavigationBar:
    """Fixed navigation bar that uses session state to prevent infinite reruns."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render(self) -> None:
        """Render navigation controls without infinite loops."""
        st.markdown("### 🎓 University Marks Manager")

        # Initialize session state for tracking changes
        if "nav_selected_year" not in st.session_state:
            st.session_state.nav_selected_year = self.controller.current_year
        if "nav_selected_semester" not in st.session_state:
            st.session_state.nav_selected_semester = None

        # Year selector - using session state to prevent loops
        self._render_year_selector()

        # Show setup mode or semester selector based on controller state
        if self.controller.is_setup_mode:
            self._render_setup_mode()
        elif self.controller.year and not self.controller.is_setup_mode:
            self._render_semester_selector()

    def _render_year_selector(self) -> None:
        """Render year selector with session state management."""
        # Get current selection
        current_year = st.session_state.nav_selected_year

        # Render selectbox
        selected_year = st.selectbox(
            "Select Academic Year",
            options=self.controller.available_years,
            index=self.controller.available_years.index(current_year),
            key="year_selector_unique",  # Unique key to prevent conflicts
        )

        # Only process change if year actually changed
        if selected_year != current_year:
            # Update session state first
            st.session_state.nav_selected_year = selected_year
            st.session_state.nav_selected_semester = None  # Reset semester

            # Update controller
            self.controller.set_year(selected_year)

            # Single rerun to reflect changes
            st.rerun()

    def _render_setup_mode(self) -> None:
        """Render setup mode interface using forms to prevent reruns."""
        st.warning(f"🎓 Setting up Academic Year {self.controller.year}")
        st.info("This year doesn't exist yet. Please select which semesters you want to create.")

        # Use form to prevent instant reruns
        with st.form("semester_setup_form_nav"):
            st.markdown("### Choose Semester Setup")

            col1, col2, col3 = st.columns(3)

            with col1:
                autumn_spring = st.form_submit_button("🍂 Autumn + Spring")

            with col2:
                sessions = st.form_submit_button("📚 Session 1 + 2")

            with col3:
                trimesters = st.form_submit_button("📅 All Trimesters")

            # Handle form submissions
            if autumn_spring:
                self._create_semesters(["Autumn", "Spring"])

            if sessions:
                self._create_semesters(["Session 1", "Session 2"])

            if trimesters:
                self._create_semesters(["Trimester 1", "Trimester 2", "Trimester 3"])

    def _render_semester_selector(self) -> None:
        """Render semester selector with session state management."""
        if not self.controller.available_semesters:
            st.warning("No semesters available for this year.")
            return

        # Get current selection
        current_semester = st.session_state.nav_selected_semester

        # Default to first semester if none selected
        if current_semester not in self.controller.available_semesters:
            current_semester = self.controller.available_semesters[0]

        # Render selectbox
        selected_semester = st.selectbox(
            "Select Semester",
            options=self.controller.available_semesters,
            index=self.controller.available_semesters.index(current_semester),
            key="semester_selector_unique",
        )

        # Only process change if semester actually changed
        if selected_semester != current_semester:
            st.session_state.nav_selected_semester = selected_semester
            self.controller.set_semester(selected_semester)

    def _create_semesters(self, semesters):
        """Helper to create semesters safely."""
        try:
            # Clear existing pending semesters
            for sem in self.controller.pending_semesters.copy():
                self.controller.remove_pending_semester(sem)

            # Add new semesters
            for semester in semesters:
                self.controller.add_pending_semester(semester)

            # Finalize setup
            if self.controller.finalize_year_setup():
                st.success(f"✅ Successfully created {len(semesters)} semesters!")
                st.rerun()
            else:
                st.error("❌ Failed to create semesters")

        except Exception as e:
            st.error(f"Error creating semesters: {str(e)}")
