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

import streamlit as st

from controller.app_controller import AppController


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

        fb_key = f"total_mark_feedback_{subject_code}"
        if fb := st.session_state.get(fb_key):
            st.success(fb)
            if st.button("Dismiss", key=f"dismiss_{fb_key}", type="secondary"):
                st.session_state.pop(fb_key, None)
                st.rerun()

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

                # Pass Supplementary (PS) option when total mark is exactly 50
                ps_flag_key = f"ps_flag_{subject_code}"
                if int(new_total_mark) == 50:
                    current_ps = st.session_state.get(ps_flag_key, False)
                    ps_cols = st.columns([2, 1])
                    with ps_cols[0]:
                        updated_ps = st.checkbox(
                            "Pass Supplementary (PS) scenario?",
                            value=current_ps,
                            help="Tick if this 50 mark represents a Pass Supplementary (PS). You'll be able to set the minimum exam weight threshold.",
                        )
                    st.session_state[ps_flag_key] = updated_ps

                    if updated_ps:
                        # Allow user to specify the enforced minimum exam weight (default 40%)
                        min_exam_weight_key = f"ps_min_exam_weight_{subject_code}"
                        default_min_exam_weight = float(st.session_state.get(min_exam_weight_key, 40.0))
                        with ps_cols[1]:
                            new_min_exam_weight = st.number_input(
                                "Min Exam %",
                                min_value=0.0,
                                max_value=100.0,
                                value=default_min_exam_weight,
                                step=1.0,
                                help="Minimum exam weight applied in PS mode (default 40).",
                            )
                        # Persist in session
                        st.session_state[min_exam_weight_key] = new_min_exam_weight
                else:
                    # Clear flag if total mark moved away from 50
                    if ps_flag_key in st.session_state:
                        st.session_state.pop(ps_flag_key)
                    # Also clear any stored min exam weight for PS
                    min_exam_weight_key = f"ps_min_exam_weight_{subject_code}"
                    if min_exam_weight_key in st.session_state:
                        st.session_state.pop(min_exam_weight_key)

            with col2:
                if st.form_submit_button("Update", type="secondary"):
                    # Perform total mark persistence using persistence helper if available
                    dp = self.controller.data_persistence
                    subject.total_mark = new_total_mark
                    # PS flag persists only in session_state; exam logic will read it when calculating
                    try:
                        if hasattr(dp, "set_total_mark"):
                            dp.set_total_mark(self.controller.semester or "", subject.subject_code, new_total_mark)  # type: ignore[attr-defined]
                        else:
                            return  # Abort if unsupported persistence
                        success, message = True, f"Total Mark for '{subject.subject_code}' set to {new_total_mark}."
                    except Exception as e:
                        success, message = False, f"Failed to set total mark: {e}"
                    if success:
                        st.session_state[fb_key] = message
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

        persistence = self.controller.data_persistence
        # Prefer DB-backed semester list if available
        if hasattr(persistence, "list_semesters"):
            existing_semesters = persistence.list_semesters()  # type: ignore[attr-defined]
        else:  # legacy fallback
            existing_semesters = list(persistence.data.keys())  # type: ignore[attr-defined]

        feedback_add_sem_key = "semester_add_feedback"
        if fb := st.session_state.get(feedback_add_sem_key):
            st.success(fb)
            if st.button("Dismiss", key="dismiss_semester_add_feedback", type="secondary"):
                st.session_state.pop(feedback_add_sem_key, None)
                st.rerun()

        feedback_remove_sem_key = "semester_remove_feedback"
        if fb := st.session_state.get(feedback_remove_sem_key):
            st.success(fb)
            if st.button("Dismiss", key="dismiss_semester_remove_feedback", type="secondary"):
                st.session_state.pop(feedback_remove_sem_key, None)
                st.rerun()

        if existing_semesters:
            # Display existing semesters in a nice format
            cols = st.columns(len(existing_semesters) if len(existing_semesters) <= 4 else 4)
            for i, semester in enumerate(existing_semesters):
                with cols[i % 4]:
                    if hasattr(persistence, "count_subjects_per_semester"):
                        # Single pass count retrieval cached per loop if needed
                        # For simplicity, compute once per semester (small list)
                        try:
                            counts_map = {name: cnt for name, cnt in persistence.count_subjects_per_semester()}  # type: ignore[attr-defined]
                            subject_count = counts_map.get(semester, 0)
                        except Exception:
                            subject_count = 0
                    else:
                        subject_count = len(getattr(persistence, "data", {}).get(semester, {}))  # type: ignore
                    st.metric(label=semester, value=f"{subject_count} subjects")
        else:
            st.info("No semesters found for this year.")
            # Offer quick initialization when no semesters exist yet
            with st.form("initialize_year_semesters_form"):
                st.markdown("**Initialize Semesters for Year**")
                default_presets = ["Autumn", "Spring", "Summer"]
                st.caption(
                    "Enter a comma separated list of semester names or use the preset buttons below. "
                    "You can still add/remove later."
                )
                semester_input = st.text_input(
                    "Semester Names",
                    placeholder=", ".join(default_presets),
                    help="Comma separated. Example: Autumn, Spring, Summer",
                )
                preset_col1, preset_col2, preset_col3 = st.columns(3)
                with preset_col1:
                    if st.form_submit_button("Use Standard", type="secondary", disabled=bool(semester_input)):
                        self._bulk_add_semesters(default_presets)
                        st.session_state[feedback_add_sem_key] = "Initialized standard semesters."
                        st.rerun()
                with preset_col2:
                    if st.form_submit_button("Annual Only", type="secondary", disabled=bool(semester_input)):
                        self._bulk_add_semesters(["Annual"])
                        st.session_state[feedback_add_sem_key] = "Initialized Annual semester."
                        st.rerun()
                with preset_col3:
                    if st.form_submit_button("Session 1&2", type="secondary", disabled=bool(semester_input)):
                        self._bulk_add_semesters(["Session 1", "Session 2"])
                        st.session_state[feedback_add_sem_key] = "Initialized Session 1 & 2 semesters."
                        st.rerun()
                if st.form_submit_button("Create Listed Semesters", type="primary"):
                    names = [s.strip() for s in semester_input.split(",") if s.strip()] or default_presets
                    self._bulk_add_semesters(names)
                    st.session_state[feedback_add_sem_key] = f"Initialized semesters: {', '.join(names)}"
                    st.rerun()

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
                        st.session_state[feedback_add_sem_key] = f"Added semester '{semester}'"
                        st.rerun()

        with col2:
            st.markdown("**Add Custom Semester:**")
            with st.form("add_custom_semester_form"):
                custom_semester = st.text_input(
                    "Semester Name", placeholder="e.g., Winter, Session 3, etc.", help="Enter a custom semester name"
                )

                if st.form_submit_button("Add Custom Semester"):
                    if custom_semester:
                        if custom_semester in (existing_semesters or []):
                            st.error(f"Semester '{custom_semester}' already exists.")
                        else:
                            self._add_semester(custom_semester)
                            st.session_state[feedback_add_sem_key] = f"Added semester '{custom_semester}'"
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
                        st.session_state[feedback_remove_sem_key] = f"Removed semester '{semester_to_remove}'"
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
            persistence = self.controller.data_persistence
            if hasattr(persistence, "add_semester"):
                persistence.add_semester(semester_name)  # type: ignore[attr-defined]
            else:
                return

            st.session_state["semester_add_feedback"] = f"Successfully added semester '{semester_name}'"

            # Update available semesters in controller by refreshing data persistence
            current_year = self.controller.year
            if current_year:
                self.controller.set_year(current_year)  # This will refresh the data

        except Exception as e:
            st.error(f"Failed to add semester: {str(e)}")

    def _bulk_add_semesters(self, semester_names: list[str]) -> None:
        """Add multiple semesters (UI helper)."""
        if not self.controller.data_persistence:
            return
        try:
            persistence = self.controller.data_persistence
            if hasattr(persistence, "add_semesters"):
                persistence.add_semesters(semester_names)  # type: ignore[attr-defined]
            else:
                # Fallback loop
                for name in semester_names:
                    if hasattr(persistence, "add_semester"):
                        persistence.add_semester(name)  # type: ignore[attr-defined]
            # Refresh controller
            current_year = self.controller.year
            if current_year:
                self.controller.set_year(current_year)
        except Exception as e:
            st.error(f"Failed to initialize semesters: {e}")

    def _remove_semester(self, semester_name: str) -> None:
        """Remove a semester from the current year.

        Args:
            semester_name: Name of the semester to remove
        """
        if not self.controller.data_persistence:
            st.error("Data persistence not available.")
            return

        try:
            persistence = self.controller.data_persistence
            if hasattr(persistence, "remove_semester"):
                if semester_name in (persistence.list_semesters() if hasattr(persistence, "list_semesters") else []):  # type: ignore[attr-defined]
                    persistence.remove_semester(semester_name)  # type: ignore[attr-defined]
                else:
                    st.error(f"Semester '{semester_name}' not found.")
            else:
                return

            # Refresh controller state
            current_year = self.controller.year
            if current_year:
                self.controller.set_year(current_year)

        except Exception as e:
            st.error(f"Failed to remove semester: {str(e)}")
