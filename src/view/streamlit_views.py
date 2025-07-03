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
        st.title("University Marks Manager")

        # Render navigation using component
        self.navigation.render()

        # Check if ready to render main content
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

            Manage Tab (➕):
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
        tab1, tab2, tab3 = st.tabs(["&#x1F4CA; Overview", "&#x2795; Manage", "&#x1F4C8; Analytics"])

        with tab1:
            # Use the overview display component
            self.overview_display.render()

        with tab2:
            self._render_manage_tab()

        with tab3:
            # Use the analytics display component
            self.analytics_display.render()

    def _render_manage_tab(self) -> None:
        """Render management tab with organized CRUD operations and settings.

        Provides a comprehensive management interface organized into logical
        sections for different types of administrative operations. The layout
        uses expandable sections and column layouts to organize functionality
        while maintaining clean visual presentation.

        Section Organization:
            Subject Management Section:
                ├── Add Subject: Form for creating new subjects
                └── Delete Subject: Interface for removing subjects

            Assignment Management Section:
                ├── Add Assignment: Form for creating new assignments
                ├── Modify Assignment: Interface for editing existing assignments
                └── Delete Assignment: Interface for removing assignments

            Settings Section:
                └── Set Total Marks: Configuration for subject target marks

        Layout Features:
            - Sectioned Organization: Logical grouping of related operations
            - Expandable Containers: Collapsible sections for organized presentation
            - Column Layouts: Efficient use of horizontal space
            - Visual Separators: Clear divisions between functional areas
            - Icon Integration: Visual indicators for different operation types

        User Experience:
            - Intuitive Organization: Related operations grouped together
            - Expandable Interface: Users can focus on specific tasks
            - Efficient Layout: Multiple operations accessible without scrolling
            - Clear Visual Hierarchy: Sections and operations clearly delineated

        Form Integration:
            - Component-Based Forms: Each operation uses specialized form components
            - Consistent Validation: Standardized error handling across all forms
            - User Feedback: Success and error messaging for all operations
            - State Management: Form state coordinated through controller

        Example:
            >>> view._render_manage_tab()
            >>> # Displays organized management interface with sections and forms
        """
        # Subject Management Section
        with st.container():
            st.markdown("### &#x1F4DA; Subject Management")
            col1, col2 = st.columns(2, gap="medium")

            with col1:
                with st.expander("&#x2795; Add Subject", expanded=True):
                    self.subject_forms.render_add_form()

            with col2:
                with st.expander("&#x1F5D1; Delete Subject", expanded=True):
                    self.subject_forms.render_delete_form()

        st.divider()

        # Assignment Management Section
        with st.container():
            st.markdown("###  &#x1F4DD; Assignment Management")
            col1, col2, col3 = st.columns(3, gap="medium")

            with col1:
                with st.expander("&#x2795; Add Assignment", expanded=True):
                    self.assignment_forms.render_add_form()

            with col2:
                with st.expander("&#x270F; Modify Assignment", expanded=True):
                    self.assignment_forms.render_modify_form()

            with col3:
                with st.expander("&#x1F5D1; Delete Assignment", expanded=True):
                    self.assignment_forms.render_delete_form()

        st.divider()

        # Settings Section
        with st.container():
            st.markdown("### &#x2699; Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("&#x1F3AF; Set Total Marks", expanded=True):
                    self.settings_forms.render_total_mark_form()
            
            with col2:
                with st.expander("&#x1F4C5; Manage Semesters", expanded=True):
                    self.settings_forms.render_semester_management_form()
