"""Analytics display components package for the University Marks Manager.

This package provides a modular analytics system for comprehensive academic
performance visualization and analysis. It represents the next-generation
analytics architecture, replacing the monolithic analytics display with
specialized, focused components.

Package Architecture:
    The analytics package implements a modular design with specialized components:

    Main Coordinator:
        - AnalyticsDisplay: Primary interface coordinator and data orchestrator

    Visualization Components:
        - GradeStatusDisplay: Grade overview, status, and progress indicators
        - AssignmentChartsDisplay: Interactive charts and assignment visualizations
        - PerformanceDisplay: Trend analysis, statistics, and performance metrics

    Management Components:
        - ExamManagementDisplay: Exam data entry, calculations, and management

Component Responsibilities:
    AnalyticsDisplay:
        - Orchestrates all analytics components and data flow
        - Manages tabbed interface and overall layout structure
        - Coordinates with AnalyticsController for data retrieval
        - Handles subject selection validation and error states

    GradeStatusDisplay:
        - Current grade status and achievement indicators
        - Assignment breakdown tables and summary metrics
        - Grade distribution charts and progress visualization
        - Mark distribution analysis and coverage metrics

    AssignmentChartsDisplay:
        - Interactive assignment performance bar charts
        - Weight distribution visualization (progress bars and pie charts)
        - Grade reference guides and performance summaries
        - Adaptive chart formatting based on data characteristics

    PerformanceDisplay:
        - Progress tracking towards grade targets (HD/D/C/P)
        - Performance trend analysis with line charts
        - Statistical metrics including averages and consistency
        - Personalized feedback and improvement suggestions

    ExamManagementDisplay:
        - Exam mark entry and modification with validation
        - Automatic exam calculation based on assignment performance
        - Exam requirements calculator with target grade analysis
        - Interactive advice system for exam preparation

Key Features:
    - Modular Architecture: Specialized components with clear responsibilities
    - Interactive Visualizations: Plotly charts with hover details and animations
    - Responsive Design: Adaptive layouts that work with different data sizes
    - Intelligent Calculations: Automatic grade and exam requirement calculations
    - User-Friendly Interface: Streamlit components with clear navigation
    - Type Safety: Comprehensive type annotations throughout

Usage Patterns:
    >>> from view.components.displays.analytics import AnalyticsDisplay
    >>> from controller.app_controller import AppController
    >>>
    >>> # Complete analytics interface
    >>> controller = AppController()
    >>> analytics = AnalyticsDisplay(controller)
    >>> analytics.render()  # Renders full tabbed analytics interface

    >>> # Individual component usage
    >>> from view.components.displays.analytics import GradeStatusDisplay
    >>> grade_display = GradeStatusDisplay(controller)
    >>> grade_display.render_overview(analytics_data)

Example:
    >>> from view.components.displays.analytics import (
    ...     AnalyticsDisplay, GradeStatusDisplay, AssignmentChartsDisplay,
    ...     PerformanceDisplay, ExamManagementDisplay
    ... )
    >>> from controller.app_controller import AppController
    >>>
    >>> # Initialize with controller
    >>> controller = AppController()
    >>>
    >>> # Full analytics interface
    >>> analytics = AnalyticsDisplay(controller)
    >>> analytics.render()
    >>>
    >>> # Or use individual components
    >>> grade_status = GradeStatusDisplay(controller)
    >>> charts = AssignmentChartsDisplay(controller)
    >>> performance = PerformanceDisplay(controller)
    >>> exam_mgmt = ExamManagementDisplay(controller)
"""

from .analytics_display import AnalyticsDisplay
from .assignment_charts_display import AssignmentChartsDisplay
from .exam_management_display import ExamManagementDisplay
from .grade_status_display import GradeStatusDisplay
from .performance_display import PerformanceDisplay

__all__ = [
    # Main coordinator - primary analytics interface
    "AnalyticsDisplay",  # Complete analytics interface coordinator
    # Visualization components - specialized display modules
    "GradeStatusDisplay",  # Grade overview and status indicators
    "AssignmentChartsDisplay",  # Interactive charts and visualizations
    "PerformanceDisplay",  # Trend analysis and performance metrics
    # Management components - data entry and interaction
    "ExamManagementDisplay",  # Exam data management and calculations
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Michael McMillan"
__description__ = "Modular analytics components for academic performance visualization"
