from typing import List

import streamlit as st

from controller.app_controller import AppController


class SemesterSetupComponent:
    """Component for setting up semesters in a new academic year."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render_semester_setup(self) -> None:
        """Render the semester setup interface for new years."""
        if not self.controller.is_setup_mode:
            return

        st.warning(f"🎓 **Setting up Academic Year {self.controller.year}**")
        st.info("This year doesn't exist yet. Please select which semesters you want to create.")

        # Default semester options
        default_semesters = [
            "Autumn",
            "Spring",
            "Summer",
            "Annual",
            "Session 1",
            "Session 2",
            "Trimester 1",
            "Trimester 2",
            "Trimester 3",
        ]

        # Use a single form to prevent infinite reruns
        with st.form("semester_setup_form", clear_on_submit=False):
            st.markdown("### 🎯 Create Semesters for This Year")

            # Quick selection buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.form_submit_button("🍂 Autumn + Spring", use_container_width=True):
                    self._setup_semesters(["Autumn", "Spring"])
                    return

            with col2:
                if st.form_submit_button("📚 Session 1 + 2", use_container_width=True):
                    self._setup_semesters(["Session 1", "Session 2"])
                    return

            with col3:
                if st.form_submit_button("📅 All Trimesters", use_container_width=True):
                    self._setup_semesters(["Trimester 1", "Trimester 2", "Trimester 3"])
                    return

            st.markdown("---")

            # Manual selection using multiselect (safer than checkboxes)
            st.markdown("**Or select individual semesters:**")
            selected_semesters = st.multiselect(
                "Choose semesters to create:",
                options=default_semesters,
                default=[],
                help="Select one or more semesters for this academic year",
            )

            # Custom semester input
            custom_semester = st.text_input(
                "Add custom semester (optional):",
                placeholder="e.g., Winter Session, Block Course",
                help="Enter a custom semester name if needed",
            )

            st.markdown("---")

            # Action buttons
            col_create, col_cancel = st.columns(2)

            with col_create:
                create_clicked = st.form_submit_button(
                    "✅ Create Selected Semesters", type="primary", use_container_width=True
                )

            with col_cancel:
                cancel_clicked = st.form_submit_button("❌ Cancel Setup", use_container_width=True)

            # Handle form submissions
            if create_clicked:
                semesters_to_create = selected_semesters.copy()

                # Add custom semester if provided
                if custom_semester and custom_semester not in semesters_to_create:
                    semesters_to_create.append(custom_semester)

                if semesters_to_create:
                    self._setup_semesters(semesters_to_create)
                else:
                    st.error("Please select at least one semester to create.")

            if cancel_clicked:
                self.controller.cancel_year_setup()
                st.rerun()

        # Show current pending semesters (outside the form)
        if self.controller.pending_semesters:
            st.markdown("### 📋 Semesters Ready to Create:")
            for semester in self.controller.pending_semesters:
                st.write(f"• {semester}")

    def _setup_semesters(self, semesters: List[str]) -> None:
        """Setup the specified semesters."""
        try:
            # Clear existing pending semesters
            for sem in self.controller.pending_semesters.copy():
                self.controller.remove_pending_semester(sem)

            # Add new semesters
            for semester in semesters:
                self.controller.add_pending_semester(semester)

            # Finalize the setup
            if self.controller.finalize_year_setup():
                st.success(f"Successfully created {len(semesters)} semesters!")
                st.rerun()
            else:
                st.error("Failed to create semesters. Please try again.")

        except Exception as e:
            st.error(f"Error during setup: {str(e)}")
