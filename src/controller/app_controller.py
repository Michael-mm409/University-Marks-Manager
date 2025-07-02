# src/controller/app_controller.py
from datetime import datetime
from typing import List, Optional

from model.domain import Semester
from model.enums import SemesterName
from model.repositories import DataPersistence


class AppController:
    """
    AppController is the main application controller following the Model-View-Controller (MVC) pattern.
    It manages the application state and coordinates interactions between the model and the view.

    Args:
        available_years (List[str]): A list of available years for selection, ranging from two years
            before the current year to two years after the current year.
        current_year (str): The current year as a default value.
        year (Optional[str]): The currently selected year.
        available_semesters (List[str]): A list of available semesters for the selected year.
        semester (Optional[str]): The currently selected semester.
        available_subjects (List[str]): A list of available subjects for the selected semester.
        semester_obj (Optional[Semester]): The semester object for the selected semester and year.
        data_persistence (Optional[DataPersistence]): The data persistence object for the selected year.

    Methods:
        __init__(data_persistence_factory=None):
            Initializes the AppController with an optional data persistence factory.
        set_year(year: str) -> None:
            Sets the selected year and reinitializes the data persistence object.
        set_semester(semester: str) -> bool:
            Sets the selected semester and reinitializes the semester object. Returns True if successful.
        is_ready() -> bool:
            Checks if the application is ready for operations by verifying that all required state
            Args are set.
        reset() -> None:
            Resets the controller state, clearing the selected year, semester, and associated objects.
        get_state_summary() -> str:
            Returns a string summarizing the current state of the controller for debugging purposes."""

    def __init__(self, data_persistence_factory=None):
        self._data_persistence_factory = data_persistence_factory or DataPersistence
        self._year: Optional[str] = None
        self._semester: Optional[str] = None
        self._data_persistence: Optional[DataPersistence] = None
        self._sem_obj: Optional[Semester] = None

    @property
    def available_years(self) -> List[str]:
        """
        Generates a list of available years as strings.
        The method calculates a range of years starting from two years before
        the current year up to two years after the current year, inclusive.

        Returns:
            List[str]: A list of years as strings, ranging from (current_year - 2)
                    to (current_year + 2).
        """

        current_year = datetime.now().year
        return [str(y) for y in range(current_year - 2, current_year + 3)]

    @property
    def current_year(self) -> str:
        """
        Get the current year as a string.

        Returns:
            str: The current year in string format.
        """

        return str(datetime.now().year)

    @property
    def year(self) -> Optional[str]:
        """
        Retrieves the academic year associated with the application.

        Returns:
            Optional[str]: The academic year as a string, or None if not set.
        """

        return self._year

    def set_year(self, year: str) -> None:
        """
        Sets the academic year for the application and updates related state.
        This method updates the current year and reinitializes the data persistence
        layer for the specified year. Additionally, it resets any dependent state
        variables such as the semester and semester object to ensure consistency
        when the year changes.
        Args:
            year (str): The academic year to set, represented as a string.
        Returns:
            None
        """

        if self._year != year:
            self._year = year
            self._data_persistence = self._data_persistence_factory(year)
            # Reset dependent state when year changes
            self._semester = None
            self._sem_obj = None

    @property
    def available_semesters(self) -> List[str]:
        """
        Retrieve the list of available semesters.
        If the `_data_persistence` attribute is not set, a default list of semesters
        (AUTUMN, SPRING, SUMMER) is returned. Otherwise, the method retrieves the
        existing semesters from the `_data_persistence` data.
        Returns:
            List[str]: A list of semester names, either from the data persistence
            layer or the default list if no data is available.
        """

        if not self._data_persistence:
            return [SemesterName.AUTUMN, SemesterName.SPRING, SemesterName.SUMMER]

        existing_semesters = list(self._data_persistence.data.keys())
        return existing_semesters or [SemesterName.AUTUMN, SemesterName.SPRING, SemesterName.SUMMER]

    @property
    def semester(self) -> Optional[str]:
        """
        Retrieves the current semester.

        Returns:
            Optional[str]: The current semester if set, otherwise None.
        """

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
        """
        Retrieve a list of available subjects for the current semester.

        Returns:
            List[str]: A list of subject names (keys) if a semester object exists,
                       otherwise an empty list.
        """

        if not self._sem_obj:
            return []
        return list(self._sem_obj.subjects.keys())

    @property
    def semester_obj(self) -> Optional[Semester]:
        """
        Retrieves the current Semester object.

        Returns:
            Optional[Semester]: The current Semester object if set, otherwise None.
        """

        return self._sem_obj

    @property
    def data_persistence(self) -> Optional[DataPersistence]:
        """
        Retrieves the data persistence instance.
        Returns:
            Optional[DataPersistence]: The instance of DataPersistence if available,
            otherwise None.
        """

        return self._data_persistence

    def is_ready(self) -> bool:
        """
        Checks if the application controller is ready for operation.
        This method verifies that all required Args of the controller
        are initialized and not None. Specifically, it checks the following:
        - `self._year`: The year attribute.
        - `self._semester`: The semester attribute.
        - `self._data_persistence`: The data persistence mechanism.
        - `self._sem_obj`: The semester object.

        Returns:
            bool: True if all required Args are initialized, False otherwise.
        """

        return all([self._year, self._semester, self._data_persistence, self._sem_obj])

    def reset(self) -> None:
        """
        Resets the internal state of the application controller.
        This method clears the stored year, semester, data persistence object,
        and semester object, effectively resetting the controller to its initial state.
        """

        self._year = None
        self._semester = None
        self._data_persistence = None
        self._sem_obj = None

    def get_state_summary(self) -> str:
        """
        Generates a summary of the current state of the application.
        Returns:
            str: A formatted string containing the following information:
                - Year: The current year.
                - Semester: The current semester.
                - DataPersistence: Indicates whether data persistence is enabled ("Yes" or "No").
                - SemesterObj: Indicates whether a semester object is present ("Yes" or "No").
                - Ready: The readiness status of the application.
        """

        return (
            f"Year: {self._year}, "
            f"Semester: {self._semester}, "
            f"DataPersistence: {'Yes' if self._data_persistence else 'No'}, "
            f"SemesterObj: {'Yes' if self._sem_obj else 'No'}, "
            f"Ready: {self.is_ready()}"
        )
