"""Main Streamlit view controller - orchestrates UI components.

This module provides the primary view controller for the University Marks Manager
application, implementing the Model-View-Controller (MVC) pattern. The StreamlitView
class orchestrates all UI components, manages page layout, and coordinates user
interactions through a clean, organized interface.

The view controller follows a component-based architecture where specialized
components handle specific UI concerns, promoting modularity, maintainability,
and separation of responsibilities across the application interface.

Classes:
    StreamlitView: Main application view controller implementing MVC pattern

Architecture:
    The StreamlitView implements a hierarchical component structure:

    Main Controller:
        └── StreamlitView: Primary view orchestration and layout management
            ├── NavigationBar: Application navigation and routing
            ├── OverviewDisplay: Subject overview and summary information
            ├── AnalyticsDisplay: Performance analytics and visualizations
            ├── SubjectForms: Subject management form components
            ├── AssignmentForms: Assignment management form components
            └── SettingsForms: Application settings and configuration

Key Features:
    - Component-Based Architecture: Modular UI components with clear responsibilities
    - MVC Pattern: Clean separation between view, model, and controller layers
    - Responsive Layout: Three-tab interface with organized content sections
    - Consistent Navigation: Integrated navigation system with state management
    - Error Handling: Graceful degradation when data is not available

Dependencies:
    - streamlit: Core UI framework for web application interface
    - controller.app_controller.AppController: Main application controller
    - view components: Specialized UI components for different application areas

Example:
    >>> from controller.app_controller import AppController
    >>> from view.streamlit_views import StreamlitView
    >>>
    >>> # Initialize and render application
    >>> controller = AppController()
    >>> view = StreamlitView(controller)
    >>> view.render()  # Renders complete application interface
"""

import streamlit as st

from controller.app_controller import AppController
from view import AnalyticsDisplay, AssignmentForms, NavigationBar, OverviewDisplay, SettingsForms, SubjectForms


class StreamlitView:
    """Main Streamlit view class implementing the MVC pattern for UI orchestration.

    This class serves as the primary view controller for the University Marks Manager
    application, coordinating all UI components and managing the overall application
    layout. It implements a component-based architecture where specialized components
    handle specific UI concerns.

    The view controller follows the dependency injection pattern, receiving the
    application controller to coordinate with business logic and data persistence
    layers. All UI components are initialized with the controller to maintain
    consistent data access patterns.

    Attributes:
        controller: Main application controller for business logic coordination
        navigation: NavigationBar component for application routing
        overview_display: OverviewDisplay component for subject summaries
        analytics_display: AnalyticsDisplay component for performance analytics
        subject_forms: SubjectForms component for subject management
        assignment_forms: AssignmentForms component for assignment management
        settings_forms: SettingsForms component for application configuration

    Layout Structure:
        Application Interface:
            ├── Title: University Marks Manager application header
            ├── Navigation: Year, semester, and subject selection controls
            ├── Content Tabs: Three-tab interface for different application areas
            │   ├── Overview Tab: Subject summaries and key metrics
            │   ├── Manage Tab: CRUD operations for subjects and assignments
            │   └── Analytics Tab: Performance analysis and visualizations
            └── Error States: Informational messages for missing data

    Design Principles:
        - Component Composition: UI built from specialized, reusable components
        - Separation of Concerns: Each component handles specific UI responsibilities
        - Dependency Injection: Controller provided to all components for consistency
        - Error Handling: Graceful degradation with informative user messages
        - Responsive Design: Organized layout that works across different screen sizes

    Example:
        >>> controller = AppController()
        >>> view = StreamlitView(controller)
        >>> view.render()
        >>> # Renders complete application with navigation, tabs, and components
    """

    def __init__(self, controller: AppController) -> None:
        """Initialize StreamlitView with application controller and UI components.

        Sets up the main view controller with all necessary UI components,
        establishing the component hierarchy and dependency injection pattern.
        Each component receives the controller for consistent data access.

        Args:
            controller: Main application controller providing business logic
                       coordination, data access, and state management

        Component Initialization:
            - NavigationBar: Application routing and state selection
            - OverviewDisplay: Subject summaries and overview information
            - AnalyticsDisplay: Performance analytics and visualizations
            - SubjectForms: Subject CRUD operations and management
            - AssignmentForms: Assignment CRUD operations and management
            - SettingsForms: Application configuration and settings

        Example:
            >>> from controller.app_controller import AppController
            >>> controller = AppController()
            >>> view = StreamlitView(controller)
        """
        self.controller = controller

        # Initialize component classes with dependency injection
        self.navigation = NavigationBar(controller)
        self.overview_display = OverviewDisplay(controller)
        self.analytics_display = AnalyticsDisplay(controller)
        self.subject_forms = SubjectForms(controller)
        self.assignment_forms = AssignmentForms(controller)
        self.settings_forms = SettingsForms(controller)

    def render(self) -> None:
        """Render the complete application interface with navigation and content.

        Orchestrates the rendering of the main application interface, including
        the application title, navigation controls, and main content areas.
        Implements conditional rendering based on application state readiness.

        Rendering Flow:
            1. Display application title and branding
            2. Render navigation controls for user selection
            3. Check controller readiness (year and semester selected)
            4. Display main content if ready, or informational message if not

        State Handling:
            - Ready State: Year and semester selected, full interface available
            - Not Ready: Missing year/semester selection, shows guidance message

        User Experience:
            - Clear application branding and title
            - Intuitive navigation flow from selection to content
            - Helpful guidance when required selections are missing
            - Seamless transition to main content when ready

        Example:
            >>> view.render()
            >>> # Displays title, navigation, and content based on state
        """
        # Restore controller state from session on rerun (Streamlit re-executes script each time)
        prev_year = st.session_state.get("_active_year")
        prev_subject = st.session_state.get("_active_subject")
        if self.controller.year is None and "year_select" in st.session_state:
            try:
                self.controller.set_year(st.session_state["year_select"])
            except Exception:
                pass
        if self.controller.semester is None and "semester_select" in st.session_state and self.controller.year:
            try:
                self.controller.set_semester(st.session_state["semester_select"])
            except Exception:
                pass

        # Detect changes and clear feedback keys if year or subject changed
        current_subject = st.session_state.get("selected_subject")
        if prev_year and self.controller.year and prev_year != self.controller.year:
            self._clear_feedback_keys()
        elif prev_subject and current_subject and prev_subject != current_subject:
            self._clear_feedback_keys()

        st.session_state["_active_year"] = self.controller.year
        st.session_state["_active_subject"] = current_subject

        st.title("University Marks Manager")

        # Render navigation using component
        self.navigation.render()

        # Check if ready to render main content
        if not self.controller.is_ready():
            # Attempt auto-select only if there are semesters and semester missing
            if self.controller.year and not self.controller.semester:
                semesters = self.controller.available_semesters
                if semesters:
                    chosen = st.session_state.get("semester_select") or semesters[0]
                    if chosen in semesters:
                        self.controller.set_semester(chosen)
                        st.session_state["semester_select"] = chosen
            if not self.controller.is_ready():
                st.info("Please select year and semester to continue.")
                return

        # Render main content
        self._render_main_content()

    def _render_main_content(self) -> None:
        """Render main application content organized in tabbed interface.

        Provides the primary content interface organized into three distinct
        tabs, each serving different user workflows and application functions.
        The tabbed interface promotes organized access to different application
        areas while maintaining context and navigation.

        Tab Organization:
            Overview Tab (📊):
                - Subject summaries and key performance metrics
                - Quick access to important information and status
                - Read-only interface for information consumption

            Manage Tab (➕;):
                - CRUD operations for subjects and assignments
                - Form-based interfaces for data entry and modification
                - Administrative functions and data management

            Analytics Tab (📈):
                - Performance analytics and trend visualizations
                - Statistical analysis and progress tracking
                - Interactive charts and data exploration

        Design Benefits:
            - Organized Workflow: Clear separation of different user tasks
            - Context Preservation: Tab-based navigation maintains user context
            - Efficient Space Usage: Organized content without overwhelming interface
            - User-Friendly Icons: Visual indicators for easy tab identification

        Example:
            >>> view._render_main_content()
            >>> # Displays three-tab interface with organized content areas
        """
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "➕ Manage", "📈 Analytics"])

        with tab1:
            # Use the overview display component
            self.overview_display.render()

        with tab2:
            self._render_manage_tab()

        with tab3:
            # Use the analytics display component
            self.analytics_display.render()

    def _render_manage_tab(self) -> None:
        """Render management tab with organized CRUD operations and settings."""

        # Subject Management Section in Expander
        st.markdown("### 📚 Subject Management")

        add_subject_column, modify_subject_column = st.columns(2, gap="medium")

        with add_subject_column:
            with st.expander("➕ **Add Subject**", expanded=True):
                self.subject_forms.render_add_form()

        with modify_subject_column:
            with st.expander("🗑️ **Delete Subject**", expanded=True):
                self.subject_forms.render_delete_form()

        st.divider()

        # Assignment Management Section (NO outer expander)
        st.markdown("### 📝 Assignment Management")
        add_assignment_column, modify_assignment_column, delete_assignment_column = st.columns(3, gap="medium")

        with add_assignment_column:
            with st.expander("➕ **Add Assignment**", expanded=False):
                self.assignment_forms.render_add_form()

        with modify_assignment_column:
            with st.expander("✏️ **Modify Assignment**", expanded=False):
                self.assignment_forms.render_modify_form()

        with delete_assignment_column:
            with st.expander("🗑️ **Delete Assignment**", expanded=False):
                self.assignment_forms.render_delete_form()

        st.divider()

        # Settings Section (not in expander)
        st.markdown("### ⚙️ Settings")
        add_assignment_column, modify_assignment_column = st.columns(2)

        with add_assignment_column:
            with st.expander("📈 Manage Total Marks", expanded=False):
                self.settings_forms.render_total_mark_form()

        with modify_assignment_column:
            with st.expander("📅 Manage Semesters", expanded=False):
                self.settings_forms.render_semester_management_form()

    def _clear_feedback_keys(self) -> None:
        """Remove any session_state feedback messages (called on year/subject change)."""
        to_delete = [
            feedback_key
            for feedback_key in list(st.session_state.keys())
            if isinstance(feedback_key, str) and (feedback_key.endswith("_feedback") or "feedback" in feedback_key)
        ]
        for key in to_delete:
            try:
                del st.session_state[key]
            except KeyError:
                pass
