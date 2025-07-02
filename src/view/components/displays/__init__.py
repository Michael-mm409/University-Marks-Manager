"""
Display components package for the University Marks Manager.

This package provides the main display components for academic data visualization
and user interface rendering. It serves as the primary entry point for all
display-related functionality in the University Marks Manager application.

Components:
    AnalyticsDisplay: Comprehensive analytics and performance visualization
    OverviewDisplay: High-level semester and subject overview interface
    SummaryDisplay: Statistical summaries and calculated metrics display

Usage:
    >>> from view.components.displays import AnalyticsDisplay, OverviewDisplay
    >>> controller = AppController()
    >>> analytics = AnalyticsDisplay(controller)
    >>> analytics.render()

Architecture:
    All components follow consistent patterns:
    - Constructor injection of AppController
    - Render methods for Streamlit UI generation
    - Modular design with separation of concerns
"""

from .analytics.analytics_display import AnalyticsDisplay  # Performance analysis and charts
from .overview_display import OverviewDisplay  # Subject listing and navigation
from .summary_display import SummaryDisplay

__all__ = [
    "AnalyticsDisplay",  # Main analytics interface
    "OverviewDisplay",  # Subject overview and management
    "SummaryDisplay",  # Statistics and summaries
]
