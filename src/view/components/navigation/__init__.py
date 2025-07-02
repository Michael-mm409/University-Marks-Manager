"""Navigation components package for the University Marks Manager.

This package provides navigation components that handle user interface navigation,
routing, and page management in the University Marks Manager application. It implements
a centralized navigation system with consistent user experience patterns and
accessibility features for academic data management workflows.

Package Structure:
    The navigation package contains the primary navigation component:

    Core Navigation:
        - NavigationBar: Main application navigation interface and routing controller

Component Responsibilities:
    NavigationBar:
        - Primary application navigation interface with menu structure
        - Page routing and state management across application sections
        - User session management and navigation context preservation
        - Responsive navigation design for different screen sizes
        - Accessibility features including keyboard navigation and screen reader support

Key Features:
    - Centralized Navigation: Single source of truth for application routing
    - State Management: Navigation state preservation across page transitions
    - User Experience: Consistent navigation patterns and visual design
    - Accessibility: Full keyboard navigation and assistive technology support
    - Responsive Design: Adaptive navigation for mobile and desktop interfaces

Design Principles:
    - Single Responsibility: Navigation component focuses solely on routing and UI navigation
    - Consistency: Standardized navigation patterns across all application pages
    - Accessibility First: Navigation designed for universal access and usability
    - State Preservation: User context and selections maintained during navigation
    - Performance: Efficient routing with minimal page reload requirements

Navigation Architecture:
    The navigation system implements a hierarchical structure:

    Navigation Structure:
        ├── Main Navigation: Primary application sections and features
        ├── Sub Navigation: Section-specific navigation and context menus
        ├── Breadcrumbs: Location awareness and quick navigation
        └── Quick Actions: Frequently used operations and shortcuts

    State Management:
        - Session State: User selections and context preservation
        - Navigation History: Back/forward navigation support
        - Page Context: Current location and available actions
        - User Preferences: Navigation customization and accessibility settings

Usage Patterns:
    >>> from view.components.navigation import NavigationBar
    >>> from controller.app_controller import AppController
    >>>
    >>> # Initialize navigation with controller
    >>> controller = AppController()
    >>> nav_bar = NavigationBar(controller)
    >>>
    >>> # Render navigation interface
    >>> nav_bar.render()  # Main navigation bar with routing
    >>> nav_bar.render_sidebar()  # Sidebar navigation for mobile
    >>> nav_bar.render_breadcrumbs()  # Location breadcrumbs

Integration:
    Navigation components integrate with:
    - Controller Layer: Page routing and business logic coordination
    - View Layer: Page rendering and component display management
    - State Management: Session state and user context preservation
    - Streamlit Framework: UI rendering and user interaction handling
    - Analytics: Navigation tracking and user behavior analysis

Accessibility Features:
    Keyboard Navigation:
        - Full keyboard accessibility with tab navigation
        - Keyboard shortcuts for common navigation actions
        - Focus management and visual focus indicators
        - Screen reader compatibility with ARIA labels

    Visual Design:
        - High contrast navigation elements for visibility
        - Responsive design for different screen sizes and orientations
        - Clear visual hierarchy and navigation structure
        - Consistent styling and interaction patterns

Performance Considerations:
    - Lazy Loading: Navigation elements loaded on demand
    - State Caching: Navigation state cached for performance
    - Minimal Reloads: Efficient page transitions without full reloads
    - Responsive Rendering: Adaptive rendering based on device capabilities

Example:
    >>> from view.components.navigation import NavigationBar
    >>> from controller.app_controller import AppController
    >>>
    >>> # Initialize navigation system
    >>> controller = AppController()
    >>> navigation = NavigationBar(controller)
    >>>
    >>> # Render main navigation
    >>> navigation.render()
    >>>
    >>> # Handle navigation events
    >>> if navigation.current_page == "analytics":
    ...     # Render analytics page content
    ...     pass
    ... elif navigation.current_page == "overview":
    ...     # Render overview page content
    ...     pass
    >>>
    >>> # Navigation state management
    >>> selected_semester = navigation.get_selected_semester()
    >>> selected_subject = navigation.get_selected_subject()
"""

from .navigation_bar import NavigationBar

__all__ = [
    "NavigationBar",  # Main application navigation interface and routing controller
]

# Package metadata
__version__ = "1.0.0"
__author__ = "University Marks Manager Team"
__description__ = "Navigation components for application routing and user interface navigation"

# Navigation capabilities
_NAVIGATION_FEATURES = {
    "routing": "Centralized page routing and navigation management",
    "state_management": "User context and selection preservation across pages",
    "accessibility": "Full keyboard navigation and screen reader support",
    "responsive_design": "Adaptive navigation for mobile and desktop interfaces",
    "user_experience": "Consistent navigation patterns and visual design",
}

# Component responsibilities
_COMPONENT_INFO = {
    "NavigationBar": {
        "type": "Core Navigation Component",
        "responsibility": "Primary application navigation and routing",
        "features": ["menu_structure", "page_routing", "state_management", "accessibility_support"],
        "integration": ["controller_layer", "view_layer", "streamlit_framework", "session_management"],
    },
}

# Navigation structure
_NAVIGATION_STRUCTURE = {
    "main_navigation": "Primary application sections and core features",
    "sub_navigation": "Section-specific menus and contextual navigation",
    "breadcrumbs": "Location awareness and hierarchical navigation",
    "quick_actions": "Frequently used operations and shortcuts",
}

# Accessibility features
_ACCESSIBILITY_FEATURES = {
    "keyboard_navigation": "Full keyboard accessibility with tab support",
    "screen_reader": "ARIA labels and semantic HTML for assistive technology",
    "visual_design": "High contrast and clear visual hierarchy",
    "responsive": "Adaptive design for different devices and orientations",
}
