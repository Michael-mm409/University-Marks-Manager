# src/controller/handlers/__init__.py
from .analytics_handler import AnalyticsHandler
from .assignment_handler import AssignmentHandler
from .subject_handler import SubjectHandler

__all__ = ["AssignmentHandler", "SubjectHandler", "AnalyticsHandler"]
