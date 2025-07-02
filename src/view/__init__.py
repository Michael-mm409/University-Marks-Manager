"""
View layer initializer.

This module aggregates and exposes core components used in the application's
Streamlit-based user interface (UI), including display components, form handlers,
navigation controls, and utility functions.

Re-exported components:
    - StreamlitView
    - NavigationBar
    - OverviewDisplay
    - AnalyticsDisplay
    - SummaryDisplay
    - SubjectForms
    - AssignmentForms
    - SettingsForms
    - safe_float
    - safe_display_value
"""

from .components.displays.analytics.analytics_display import AnalyticsDisplay
from .components.displays.overview_display import OverviewDisplay
from .components.displays.summary_display import SummaryDisplay
from .components.forms.assignment_forms import AssignmentForms
from .components.forms.settings_forms import SettingsForms
from .components.forms.subject_forms import SubjectForms
from .components.navigation.navigation_bar import NavigationBar
from .streamlit_views import StreamlitView
from .utils.formatters import safe_display_value, safe_float

__all__ = [
    "StreamlitView",
    "NavigationBar",
    "OverviewDisplay",
    "AnalyticsDisplay",
    "SummaryDisplay",
    "SubjectForms",
    "AssignmentForms",
    "SettingsForms",
    "safe_float",
    "safe_display_value",
]
