"""Minimal StreamlitView to test without complex components."""

import streamlit as st

from controller.app_controller import AppController


class MinimalStreamlitView:
    """Minimal view for testing."""

    def __init__(self, controller: AppController):
        self.controller = controller

    def render(self) -> None:
        """Render minimal interface."""
        st.title("University Marks Manager")

        # Simple year selection (copy from debug_minimal.py)
        st.markdown("### Select Year")
        selected_year = st.selectbox(
            "Academic Year",
            options=self.controller.available_years,
            index=self.controller.available_years.index(self.controller.current_year),
        )

        if selected_year != self.controller.year:
            self.controller.set_year(selected_year)
            st.write(f"Year set to: {self.controller.year}")
            st.write(f"Setup mode: {self.controller.is_setup_mode}")

        # Handle setup mode manually
        if self.controller.is_setup_mode:
            st.warning(f"Setting up {self.controller.year}")

            with st.form("simple_setup"):
                st.write("This year needs semesters. Choose a preset:")

                col1, col2 = st.columns(2)
                with col1:
                    autumn_spring = st.form_submit_button("Autumn + Spring")
                with col2:
                    sessions = st.form_submit_button("Session 1 + 2")

                if autumn_spring:
                    self.controller.add_pending_semester("Autumn")
                    self.controller.add_pending_semester("Spring")
                    if self.controller.finalize_year_setup():
                        st.success("Created semesters!")
                        st.rerun()

                if sessions:
                    self.controller.add_pending_semester("Session 1")
                    self.controller.add_pending_semester("Session 2")
                    if self.controller.finalize_year_setup():
                        st.success("Created semesters!")
                        st.rerun()

        # Show semester selection if not in setup mode
        elif self.controller.year and not self.controller.is_setup_mode:
            st.markdown("### Select Semester")
            if self.controller.available_semesters:
                selected_semester = st.selectbox("Semester", options=self.controller.available_semesters)

                if self.controller.set_semester(selected_semester):
                    st.success(f"Semester set to: {self.controller.semester}")

                    # Show placeholder for main content
                    st.markdown("### 🎉 Main Content Would Go Here")

                    # Simple tabs placeholder
                    tab1, tab2, tab3 = st.tabs(["📊 Overview", "➕ Manage", "📈 Analytics"])

                    with tab1:
                        st.write("Overview content would go here")
                    with tab2:
                        st.write("Management forms would go here")
                    with tab3:
                        st.write("Analytics would go here")
            else:
                st.warning("No semesters available")
