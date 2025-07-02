"""Main analytics display coordinator.

This module coordinates the rendering of all analytics components in the University
Marks Manager. It acts as the primary orchestrator for the analytics tab, managing
data flow between the analytics controller and specialized display components.

The analytics display is organized into several sections:
    1. Grade Status Overview - Current grade and metrics
    2. Assignment Breakdown - Detailed assignment table and summary
    3. Visual Analytics Tabs - Charts and performance visualizations
    4. Exam Management - Exam data input and display

Architecture:
    AnalyticsDisplay (coordinator)
    ├── AnalyticsController (data provider)
    └── Display Components:
        ├── GradeStatusDisplay (overview and charts)
        ├── AssignmentChartsDisplay (assignment visualizations)
        ├── PerformanceDisplay (performance analysis)
        └── ExamManagementDisplay (exam data management)

Example:
    >>> from controller.app_controller import AppController
    >>> controller = AppController()
    >>> display = AnalyticsDisplay(controller)
    >>> display.render()  # Renders complete analytics interface
"""

from typing import Any, Dict, Optional

import streamlit as st

from controller.analytics_controller import AnalyticsController
from controller.app_controller import AppController

from .assignment_charts_display import AssignmentChartsDisplay
from .exam_management_display import ExamManagementDisplay
from .grade_status_display import GradeStatusDisplay
from .performance_display import PerformanceDisplay


class AnalyticsDisplay:
    """Coordinates analytics tab display components.

    This class serves as the main coordinator for the analytics interface,
    orchestrating data retrieval and delegating rendering to specialized
    display components. It follows the coordinator pattern to maintain
    separation of concerns between data management and presentation.

    The class manages the overall layout structure and ensures consistent
    data flow to all sub-components while maintaining responsive design
    principles for the Streamlit interface.

    Attributes:
        controller: Main application controller for data access
        analytics_controller: Specialized controller for analytics data
        grade_status: Component for grade overview and status displays
        assignment_charts: Component for assignment visualization charts
        performance: Component for performance analysis and metrics
        exam_management: Component for exam data input and management

    Example:
        >>> controller = AppController()
        >>> analytics = AnalyticsDisplay(controller)
        >>> analytics.render()
    """

    def __init__(self, controller: AppController) -> None:
        """Initialize analytics display with required controllers and components.

        Args:
            controller: Main application controller providing data access
        """
        self.controller: AppController = controller
        self.analytics_controller: AnalyticsController = AnalyticsController(controller)
        self.grade_status: GradeStatusDisplay = GradeStatusDisplay(controller)
        self.assignment_charts: AssignmentChartsDisplay = AssignmentChartsDisplay(controller)
        self.performance: PerformanceDisplay = PerformanceDisplay(controller)
        self.exam_management: ExamManagementDisplay = ExamManagementDisplay(controller)

    def render(self) -> None:
        """Render the complete analytics interface.

        Orchestrates the rendering of all analytics components in a structured
        layout. Handles subject selection validation and error states gracefully.

        Layout Structure:
            1. Subject validation and data loading
            2. Grade status overview section
            3. Assignment breakdown table
            4. Visual analytics tabs (charts and analysis)
            5. Exam management interface

        State Management:
            - Validates selected subject from session state
            - Loads analytics data through controller
            - Handles error states for missing data
            - Provides user feedback for selection requirements

        Example:
            >>> display.render()  # Renders full analytics interface
        """
        selected_subject: Optional[Any] = st.session_state.get("selected_subject")
        if not selected_subject:
            st.info("&#x1F4CB; Select a subject from the sidebar to view detailed analytics")
            return

        # Get analytics data with corrected grade distribution
        # FIX: Use Optional type since get_subject_analytics can return None
        analytics_data: Optional[Dict[str, Any]] = self.analytics_controller.get_subject_analytics(selected_subject)
        if not analytics_data:
            st.error("&#x274C; Unable to load analytics data for the selected subject")
            st.info("&#x1F4A1; Try refreshing the page or selecting a different subject")
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

    def _render_visual_analytics(self, analytics_data: Dict[str, Any]) -> None:
        """Render visual analytics section with tabbed interface.

        Creates a tabbed interface for different types of visual analytics,
        allowing users to explore data through multiple visualization approaches.
        Each tab focuses on a specific aspect of academic performance analysis.

        Args:
            analytics_data: Complete analytics dataset for the selected subject

        Tab Structure:
            - Grade Overview: Current grade status and progress visualization
            - Assignment Progress: Individual assignment performance charts
            - Performance Analysis: Statistical analysis and trends

        Design Notes:
            - Uses Streamlit tabs for clean organization
            - Each tab delegates to specialized display components
            - Maintains consistent data passing to all components

        Example:
            >>> self._render_visual_analytics(analytics_data)
        """
        st.subheader("&#x1F4C8; Visual Analytics")

        tab1, tab2, tab3 = st.tabs(
            ["&#x1F4CA; Grade Overview", "&#x1F4CB; Assignment Progress", "&#x1F3AF; Performance Analysis"]
        )

        with tab1:
            # Grade status charts and progress indicators
            self.grade_status.render_grade_charts(analytics_data)

        with tab2:
            # Assignment performance charts and distribution
            self.assignment_charts.render(analytics_data)

        with tab3:
            # Statistical analysis and performance metrics
            self.performance.render(analytics_data)
