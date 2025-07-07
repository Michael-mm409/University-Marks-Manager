# src/view/components/forms/settings_forms.py
"""Settings and configuration form components.

This module provides form components for managing application settings, configuration
options, and administrative functions in the University Marks Manager. It implements
specialized forms for subject settings, semester-wide configuration, and data
management operations.

The SettingsForms class encapsulates all settings-related user interfaces with
proper validation, error handling, and user feedback mechanisms. It follows the
single responsibility principle by focusing specifically on configuration and
administrative form operations.

Classes:
    SettingsForms: Main settings form handler with configuration interfaces

Dependencies:
    - streamlit: UI framework for form rendering and user interaction
    - controller.set_total_mark: Business logic for total mark updates
    - controller.app_controller.AppController: Main application controller

Example:
    >>> from view.components.forms.settings_forms import SettingsForms
    >>> from controller.app_controller import AppController
    >>>
    >>> controller = AppController()
    >>> settings_forms = SettingsForms(controller)
    >>> settings_forms.render_total_mark_form()
"""

from typing import Dict

import streamlit as st

from controller import set_total_mark
from controller.app_controller import AppController
from model.domain.entities import Subject


class SettingsForms:
    """Handles settings-related form components for the University Marks Manager.

    This class provides a collection of form interfaces for managing application
    settings, subject configuration, and administrative functions. It implements
    a consistent form architecture with validation, error handling, and user
    feedback across all configuration operations.

    The class follows the dependency injection pattern, receiving the application
    controller to coordinate with business logic and data persistence layers.
    All forms implement proper validation and provide clear user feedback for
    both success and error scenarios.

    Attributes:
        controller: Main application controller for data access and business logic

    Form Categories:
        Subject Settings: Individual subject configuration and mark management
        Semester Settings: Semester-wide configuration and information display
        Data Management: Export, import, and backup functionality

    Design Principles:
        - Single Responsibility: Focused on settings and configuration forms
        - Dependency Injection: Controller provided for business logic access
        - Validation First: Input validation before processing
        - User Feedback: Clear success and error messaging
        - Error Handling: Graceful degradation with informative messages

    Example:
        >>> controller = AppController()
        >>> settings = SettingsForms(controller)
        >>> settings.render_total_mark_form()  # Subject mark configuration
        >>> settings.render_semester_settings_form()  # Semester information
        >>> settings.render_data_management_form()  # Data operations
    """

    def __init__(self, controller: AppController) -> None:
        """Initialize SettingsForms with application controller dependency.

        Sets up the settings form handler with access to the main application
        controller for business logic coordination and data operations.

        Args:
            controller: Main application controller providing data access,
                       business logic coordination, and persistence operations

        Example:
            >>> from controller.app_controller import AppController
            >>> controller = AppController()
            >>> settings_forms = SettingsForms(controller)
        """
        self.controller = controller

    def render_total_mark_form(self) -> None:
        """Render total mark configuration form for the selected subject.

        Provides a compact form interface for updating a subject's total mark
        target. The form includes validation for mark ranges (0-100), displays
        the current total mark value, and provides immediate feedback for
        successful updates or validation errors.

        Form Features:
            - Number input with range validation (0.0-100.0)
            - Current value display for reference
            - Real-time validation and error feedback
            - Automatic UI refresh after successful updates
            - Graceful error handling for missing data

        Validation Rules:
            - Subject must be selected in session state
            - Controller must be properly initialized
            - Subject must exist in current semester
            - Mark must be between 0.0 and 100.0

        User Interface:
            - Two-column layout: input field and submit button
            - Help text showing current total mark value
            - Success/error messages with appropriate styling
            - Form rerun after successful submission

        Error Handling:
            - Info message if no subject is selected
            - Error message if controller is not initialized
            - Warning if selected subject is not found
            - Error feedback for business logic validation failures

        Example:
            >>> settings_forms.render_total_mark_form()
            >>> # Displays form for currently selected subject
            >>> # User can update total mark with validation
        """
        subject_code = st.session_state.get("selected_subject")
        if not subject_code:
            st.info("Select a subject first")
            return

        if not self.controller.semester_obj or not self.controller.data_persistence:
            st.error("Controller not properly initialized.")
            return

        subject = self.controller.semester_obj.subjects.get(subject_code)
        if not subject:
            st.warning("Subject not found.")
            return

        with st.form(f"set_total_mark_compact_{subject_code}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                new_total_mark = st.number_input(
                    f"Total Mark for {subject_code}",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(subject.total_mark),
                    step=0.01,
                    help=f"Current: {subject.total_mark}",
                )

            with col2:
                if st.form_submit_button("Update", type="secondary"):
                    success, message = set_total_mark(subject, new_total_mark, self.controller.data_persistence)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    def render_semester_settings_form(self) -> None:
        """Render semester-wide settings and information display.

        Provides a read-only information panel showing current semester details
        and statistics. This form serves as an information dashboard for
        semester-wide configuration and provides context for other settings.

        Display Components:
            - Current academic year information
            - Semester name and session details
            - Total subject count metric
            - Two-column layout for organized information display

        Information Categories:
            Academic Session:
                - Current year display
                - Semester name (Session 1, Session 2, etc.)

            Statistics:
                - Total number of subjects in semester
                - Future: Additional semester-wide metrics

        Error Handling:
            - Error message if semester object is not initialized
            - Graceful degradation with informative feedback

        Future Enhancements:
            - Semester name editing capability
            - Academic year modification
            - Additional semester-wide statistics
            - Configuration export/import for semester settings

        Example:
            >>> settings_forms.render_semester_settings_form()
            >>> # Displays current semester information
            >>> # Shows year, name, and subject count
        """
        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        st.markdown("#### Semester Settings")

        current_year_column, subject_count_column = st.columns(2)

        with current_year_column:
            st.info(f"**Current Year:** {self.controller.semester_obj.year}")
            st.info(f"**Current Semester:** {self.controller.semester_obj.name}")

        with subject_count_column:
            total_subjects = len(self.controller.semester_obj.subjects)
            st.metric("Total Subjects", total_subjects)

    def render_data_management_form(self) -> None:
        """Render data export, import, and backup management form.

        Provides administrative functions for data management operations including
        export, import, and backup functionality. Currently displays placeholder
        interfaces with informational messages about future implementation.

        Planned Features:
            Data Export:
                - Export semester data to JSON format
                - Export individual subject data
                - Custom export filters and options
                - Multiple export formats (JSON, CSV, Excel)

            Data Backup:
                - Automatic backup creation before major operations
                - Manual backup triggering
                - Backup restoration functionality
                - Backup file management and cleanup

            Data Import:
                - Import data from external sources
                - Validation and conflict resolution
                - Batch import operations
                - Import format validation

        Current Implementation:
            - Two-column layout with export and backup buttons
            - Placeholder functionality with user notifications
            - Secondary button styling for future operations
            - Information messages about development status

        Error Handling:
            - Error message if semester is not initialized
            - Future: Comprehensive validation for import/export operations
            - Future: Error recovery for failed backup operations

        Security Considerations:
            - Future: User confirmation for destructive operations
            - Future: Data validation before import operations
            - Future: Backup integrity verification

        Example:
            >>> settings_forms.render_data_management_form()
            >>> # Displays data management interface
            >>> # Shows placeholder export/backup buttons
        """
        if not self.controller.semester_obj:
            st.error("Semester not initialized.")
            return

        st.markdown("#### Data Management")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Export Data", type="secondary"):
                # Future implementation for data export
                st.info("Export functionality coming soon!")

        with col2:
            if st.button("Backup Data", type="secondary"):
                # Future implementation for data backup
                st.info("Backup functionality coming soon!")

    def render_semester_management_form(self) -> None:
        """Render semester management form for adding/removing semesters.

        Provides comprehensive semester management functionality allowing users to:
        - View all existing semesters for the current year
        - Add new semesters (predefined or custom names)
        - Remove existing semesters (with data protection warnings)

        Form Features:
            - Current semesters display with subject counts
            - Quick-add buttons for standard semesters (Autumn, Spring, Summer)
            - Custom semester name input for non-standard sessions
            - Semester removal with confirmation and data warnings
            - Real-time updates to semester list

        Data Management:
            - Automatic data persistence for new semesters
            - Data preservation warnings for semester removal
            - Integration with AppController for state management

        Error Handling:
            - Validation for duplicate semester names
            - Error messages for invalid semester operations
            - Graceful handling of data persistence failures

        Example:
            >>> settings_forms.render_semester_management_form()
            >>> # Displays semester management interface
            >>> # Allows adding/removing semesters for current year
        """
        if not self.controller.data_persistence:
            st.error("Year not selected. Please select a year first.")
            return

        st.markdown("#### Semester Management")

        current_year = self.controller.year
        if not current_year:
            st.error("No year selected.")
            return

        # Display current semesters
        st.write(f"**Managing semesters for {current_year}:**")

        existing_semesters = list(self.controller.data_persistence.data.keys())

        if existing_semesters:
            # Display existing semesters in a nice format
            cols = st.columns(len(existing_semesters) if len(existing_semesters) <= 4 else 4)
            for i, semester in enumerate(existing_semesters):
                with cols[i % 4]:
                    subject_count = len(self.controller.data_persistence.data.get(semester, {}))
                    st.metric(label=semester, value=f"{subject_count} subjects", delta=None)
        else:
            st.info("No semesters found for this year.")

        st.divider()

        # Add semester section
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Add Standard Semester:**")
            standard_semesters = ["Autumn", "Spring", "Summer", "Annual"]

            for semester in standard_semesters:
                if semester not in existing_semesters:
                    if st.button(f"Add {semester}", key=f"add_{semester}"):
                        self._add_semester(semester)
                        st.rerun()

        with col2:
            st.markdown("**Add Custom Semester:**")
            with st.form("add_custom_semester_form"):
                custom_semester = st.text_input(
                    "Semester Name", placeholder="e.g., Winter, Session 3, etc.", help="Enter a custom semester name"
                )

                if st.form_submit_button("Add Custom Semester"):
                    if custom_semester:
                        if custom_semester in existing_semesters:
                            st.error(f"Semester '{custom_semester}' already exists.")
                        else:
                            self._add_semester(custom_semester)
                            st.success(f"Added semester '{custom_semester}'")
                            st.rerun()
                    else:
                        st.error("Please enter a semester name.")

        # Remove semester section
        if existing_semesters:
            st.divider()
            st.markdown("**Remove Semester:**")
            st.warning("⚠️ Removing a semester will permanently delete all its data!")

            with st.form("remove_semester_form"):
                semester_to_remove = st.selectbox(
                    "Select Semester to Remove",
                    options=existing_semesters,
                    help="Choose a semester to remove (this cannot be undone)",
                )

                confirm_removal = st.checkbox(
                    f"I understand that removing '{semester_to_remove}' will permanently delete all its data",
                    help="Check this box to confirm you want to remove the semester",
                )

                if st.form_submit_button("Remove Semester", type="secondary"):
                    if confirm_removal:
                        self._remove_semester(semester_to_remove)
                        st.success(f"Removed semester '{semester_to_remove}'")
                        st.rerun()
                    else:
                        st.error("Please confirm that you want to remove the semester.")

    def _add_semester(self, semester_name: str) -> None:
        """Add a new semester to the current year.

        Args:
            semester_name: Name of the semester to add
        """
        if not self.controller.data_persistence:
            st.error("Data persistence not available.")
            return

        try:
            # Add empty semester data (explicitly typed as Dict[str, Subject])
            empty_semester: Dict[str, Subject] = {}
            self.controller.data_persistence.data[semester_name] = empty_semester

            # Save the updated data
            self.controller.data_persistence.save_data(self.controller.data_persistence.data)

            st.success(f"Successfully added semester '{semester_name}'")

            # Update available semesters in controller by refreshing data persistence
            current_year = self.controller.year
            if current_year:
                self.controller.set_year(current_year)  # This will refresh the data

        except Exception as e:
            st.error(f"Failed to add semester: {str(e)}")

    def _remove_semester(self, semester_name: str) -> None:
        """Remove a semester from the current year.

        Args:
            semester_name: Name of the semester to remove
        """
        if not self.controller.data_persistence:
            st.error("Data persistence not available.")
            return

        try:
            if semester_name in self.controller.data_persistence.data:
                # Remove the semester data
                del self.controller.data_persistence.data[semester_name]

                # Save the updated data
                self.controller.data_persistence.save_data(self.controller.data_persistence.data)

                # Update available semesters in controller by refreshing data persistence
                current_year = self.controller.year
                if current_year:
                    self.controller.set_year(current_year)  # This will refresh the data

            else:
                st.error(f"Semester '{semester_name}' not found.")

        except Exception as e:
            st.error(f"Failed to remove semester: {str(e)}")
