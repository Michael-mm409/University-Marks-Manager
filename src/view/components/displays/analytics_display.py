"""Analytics tab display components - simplified coordinator."""

from controller.app_controller import AppController

# Import the new analytics system
from view.components.displays.analytics.analytics_display import AnalyticsDisplay as NewAnalyticsDisplay


class AnalyticsDisplay:
    """Legacy wrapper for the new analytics system."""

    def __init__(self, controller: AppController):
        self.new_analytics = NewAnalyticsDisplay(controller)

    def render(self) -> None:
        """Render using the new analytics system."""
        self.new_analytics.render()
