"""Main analytics display coordinator."""

import streamlit as st

from controller.analytics_controller import AnalyticsController
from controller.app_controller import AppController

from .assignment_charts_display import AssignmentChartsDisplay
from .exam_management_display import ExamManagementDisplay
from .grade_status_display import GradeStatusDisplay
from .performance_display import PerformanceDisplay


class AnalyticsDisplay:
    """Coordinates analytics tab display components."""

    def __init__(self, controller: AppController):
        self.controller = controller
        self.analytics_controller = AnalyticsController(controller)
        self.grade_status = GradeStatusDisplay(controller)
        self.assignment_charts = AssignmentChartsDisplay(controller)
        self.performance = PerformanceDisplay(controller)
        self.exam_management = ExamManagementDisplay(controller)

    def render(self) -> None:
        """Render analytics tab with all components."""
        selected_subject = st.session_state.get("selected_subject")
        if not selected_subject:
            st.info("Select a subject to view analytics")
            return

        # Get analytics data with corrected grade distribution
        analytics_data = self.analytics_controller.get_subject_analytics(selected_subject)
        if not analytics_data:
            st.error("Unable to load analytics data")
            return

        # Main grade status overview
        self.grade_status.render_overview(analytics_data)
        st.divider()

        # Assignment breakdown
        self.grade_status.render_assignment_breakdown(analytics_data)
        st.divider()

        # Visual analytics tabs
        self._render_visual_analytics(analytics_data)
        st.divider()

        # Exam management
        self.exam_management.render(analytics_data)

    def _render_visual_analytics(self, analytics_data: dict) -> None:
        """Render visual analytics tabs."""
        st.subheader("📈 Visual Analytics")

        tab1, tab2, tab3 = st.tabs(["📊 Grade Overview", "📋 Assignment Progress", "🎯 Performance Analysis"])

        with tab1:
            self.grade_status.render_grade_charts(analytics_data)

        with tab2:
            self.assignment_charts.render(analytics_data)

        with tab3:
            self.performance.render(analytics_data)
