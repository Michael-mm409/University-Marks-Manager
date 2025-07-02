# src/controller/app_controller.py
from datetime import datetime
from typing import List, Optional

from model.domain import Semester
from model.enums import SemesterName
from model.repositories import DataPersistence


class AppController:
    """
    Main application controller following MVC pattern.
    Manages application state and coordinates between model and view.
    """

    def __init__(self, data_persistence_factory=None):
        self._data_persistence_factory = data_persistence_factory or DataPersistence
        self._year: Optional[str] = None
        self._semester: Optional[str] = None
        self._data_persistence: Optional[DataPersistence] = None
        self._sem_obj: Optional[Semester] = None

    @property
    def available_years(self) -> List[str]:
        """Get list of available years."""
        current_year = datetime.now().year
        return [str(y) for y in range(current_year - 2, current_year + 3)]

    @property
    def current_year(self) -> str:
        """Get current year as default."""
        return str(datetime.now().year)

    @property
    def year(self) -> Optional[str]:
        """Get selected year."""
        return self._year

    def set_year(self, year: str) -> None:
        """Set year and reinitialize data persistence."""
        if self._year != year:
            self._year = year
            self._data_persistence = self._data_persistence_factory(year)
            # Reset dependent state when year changes
            self._semester = None
            self._sem_obj = None

    @property
    def available_semesters(self) -> List[str]:
        """Get available semesters for current year."""
        if not self._data_persistence:
            return [SemesterName.AUTUMN, SemesterName.SPRING, SemesterName.SUMMER]

        existing_semesters = list(self._data_persistence.data.keys())
        return existing_semesters or [SemesterName.AUTUMN, SemesterName.SPRING, SemesterName.SUMMER]

    @property
    def semester(self) -> Optional[str]:
        """Get selected semester."""
        return self._semester

    def set_semester(self, semester: str) -> bool:
        """
        Set semester and reinitialize semester object.

        Returns:
            bool: True if semester was set successfully, False otherwise
        """
        # Direct validation - ensures both values are not None
        if self._year is None or self._data_persistence is None:
            return False

        if self._semester != semester:
            self._semester = semester
            # Type checker now knows these are not None due to explicit checks above
            self._sem_obj = Semester(semester, self._year, self._data_persistence)

        return True

    @property
    def available_subjects(self) -> List[str]:
        """Get available subjects for current semester."""
        if not self._sem_obj:
            return []
        return list(self._sem_obj.subjects.keys())

    @property
    def semester_obj(self) -> Optional[Semester]:
        """Get semester object."""
        return self._sem_obj

    @property
    def data_persistence(self) -> Optional[DataPersistence]:
        """Get data persistence object."""
        return self._data_persistence

    def is_ready(self) -> bool:
        """Check if app is ready for operations."""
        return all([self._year, self._semester, self._data_persistence, self._sem_obj])

    def reset(self) -> None:
        """Reset controller state."""
        self._year = None
        self._semester = None
        self._data_persistence = None
        self._sem_obj = None

    def get_state_summary(self) -> str:
        """Get current state for debugging."""
        return (
            f"Year: {self._year}, "
            f"Semester: {self._semester}, "
            f"DataPersistence: {'Yes' if self._data_persistence else 'No'}, "
            f"SemesterObj: {'Yes' if self._sem_obj else 'No'}, "
            f"Ready: {self.is_ready()}"
        )
