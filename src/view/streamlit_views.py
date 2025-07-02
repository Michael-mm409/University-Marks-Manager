"""Main Streamlit view controller - orchestrates UI components."""

import streamlit as st

from controller.app_controller import AppController
from view import AnalyticsDisplay, AssignmentForms, NavigationBar, OverviewDisplay, SettingsForms, SubjectForms


class StreamlitView:
    """Main Streamlit view class following MVC pattern."""

    def __init__(self, controller: AppController):
        self.controller = controller

        # Initialize component classes
        self.navigation = NavigationBar(controller)
        self.overview_display = OverviewDisplay(controller)
        self.analytics_display = AnalyticsDisplay(controller)
        self.subject_forms = SubjectForms(controller)
        self.assignment_forms = AssignmentForms(controller)
        self.settings_forms = SettingsForms(controller)

    def render(self) -> None:
        """Render the main application interface."""
        st.title("University Marks Manager")

        # Render navigation using component
        self.navigation.render()

        # Check if ready to render main content
        if not self.controller.is_ready():
            st.info("Please select year and semester to continue.")
            return

        # Render main content
        self._render_main_content()

    def _render_main_content(self) -> None:
        """Render main application content with tabs."""
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "➕ Manage", "📈 Analytics"])

        with tab1:
            # Use the overview display component
            self.overview_display.render()

        with tab2:
            self._render_manage_tab()

        with tab3:
            # Use the analytics display component
            self.analytics_display.render()

    def _render_manage_tab(self) -> None:
        """Render management tab with organized sections using components."""
        # Subject Management Section
        with st.container():
            st.markdown("### 📚 Subject Management")
            col1, col2 = st.columns(2, gap="medium")

            with col1:
                with st.expander("➕ Add Subject", expanded=True):
                    self.subject_forms.render_add_form()

            with col2:
                with st.expander("🗑️ Delete Subject", expanded=True):
                    self.subject_forms.render_delete_form()

        st.divider()

        # Assignment Management Section
        with st.container():
            st.markdown("### 📝 Assignment Management")
            col1, col2, col3 = st.columns(3, gap="medium")

            with col1:
                with st.expander("➕ Add Assignment", expanded=True):
                    self.assignment_forms.render_add_form()

            with col2:
                with st.expander("✏️ Modify Assignment", expanded=True):
                    self.assignment_forms.render_modify_form()

            with col3:
                with st.expander("🗑️ Delete Assignment", expanded=True):
                    self.assignment_forms.render_delete_form()

        st.divider()

        # Settings Section
        with st.container():
            st.markdown("### ⚙️ Settings")
            with st.expander("🎯 Set Total Marks", expanded=True):
                self.settings_forms.render_total_mark_form()
