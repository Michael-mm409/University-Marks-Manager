"""Form components package for the University Marks Manager.

This package provides specialized form components that handle user input and data
collection in the University Marks Manager application. Each form class encapsulates
specific input scenarios with validation, error handling, and user experience
optimization for academic data management.

Package Structure:
    The forms package contains three primary form component types:

    Academic Data Forms:
        - SubjectForms: Subject creation, modification, and management forms
        - AssignmentForms: Assignment data entry and editing interfaces

    Configuration Forms:
        - SettingsForms: Application settings and preference management

Form Responsibilities:
    SubjectForms:
        - Subject creation wizard with validation
        - Subject editing forms with existing data population
        - Subject deletion confirmation dialogs
        - Bulk subject import and export interfaces
        - Subject code and name validation with academic standards

    AssignmentForms:
        - Assignment creation forms with mark and weight validation
        - Assignment editing interfaces with grade type selection
        - Batch assignment entry for multiple assessments
        - Assignment deletion with impact analysis
        - Mark entry validation and business rule enforcement

    SettingsForms:
        - Application preference configuration interfaces
        - Grade scale and marking scheme customization
        - Data import/export settings and file path configuration
        - User interface theme and display preference forms
        - Semester naming and academic calendar configuration

Key Features:
    - Input Validation: Real-time validation with clear error messaging
    - User Experience: Intuitive form layouts with helpful guidance
    - Data Integrity: Business rule enforcement at the form level
    - Error Handling: Comprehensive error feedback and recovery options
    - Accessibility: Streamlit component integration with responsive design

Design Principles:
    - Single Responsibility: Each form handles one specific data collection scenario
    - Validation First: Input validation occurs before data processing
    - User Feedback: Clear success and error messaging for all operations
    - Consistency: Standardized form layouts and interaction patterns
    - Accessibility: Intuitive interfaces suitable for academic users

Form Architecture:
    All form components follow a consistent architecture pattern:

    Form Structure:
        ├── Input Collection: Streamlit widgets for data entry
        ├── Validation Layer: Real-time input validation and feedback
        ├── Business Logic: Form-specific processing and transformation
        ├── Error Handling: User-friendly error messages and recovery
        └── Success Actions: Data submission and user confirmation

    Validation Strategy:
        - Client-side validation for immediate feedback
        - Business rule validation before data processing
        - Cross-field validation for related inputs
        - Error message localization and clarity

Usage Patterns:
    >>> from view.components.forms import SubjectForms, AssignmentForms, SettingsForms
    >>> from controller.app_controller import AppController
    >>>
    >>> # Initialize forms with controller
    >>> controller = AppController()
    >>> subject_forms = SubjectForms(controller)
    >>> assignment_forms = AssignmentForms(controller)
    >>> settings_forms = SettingsForms(controller)
    >>>
    >>> # Render specific forms
    >>> subject_forms.render_create_form()
    >>> assignment_forms.render_edit_form(assignment_data)
    >>> settings_forms.render_preferences()

Integration:
    Form components integrate with:
    - Controller Layer: Data processing and business logic coordination
    - Model Layer: Domain entity creation and validation
    - Repository Layer: Data persistence and retrieval operations
    - Validation Services: Business rule enforcement and data integrity
    - Streamlit Framework: UI rendering and user interaction handling

Validation Features:
    Input Validation:
        - Real-time validation with immediate feedback
        - Format validation for codes, names, and numeric inputs
        - Range validation for marks, weights, and percentages
        - Required field validation with clear indicators

    Business Rule Validation:
        - Academic constraints (marks ≤ maximum values)
        - Uniqueness validation (subject codes, assignment names)
        - Consistency validation (weights sum to 100%)
        - Data integrity validation across related fields

User Experience Features:
    - Progressive Disclosure: Complex forms broken into manageable steps
    - Auto-save: Draft data preservation during form completion
    - Contextual Help: Inline guidance and validation messages
    - Keyboard Navigation: Full keyboard accessibility support
    - Responsive Design: Adaptive layouts for different screen sizes

Example:
    >>> from view.components.forms import SubjectForms, AssignmentForms, SettingsForms
    >>> from controller.app_controller import AppController
    >>>
    >>> # Initialize with controller dependency
    >>> controller = AppController()
    >>>
    >>> # Subject management forms
    >>> subject_forms = SubjectForms(controller)
    >>> subject_forms.render_create_form()  # New subject creation
    >>> subject_forms.render_edit_form("CSCI251")  # Edit existing subject
    >>>
    >>> # Assignment data entry forms
    >>> assignment_forms = AssignmentForms(controller)
    >>> assignment_forms.render_add_form("CSCI251")  # Add assignment to subject
    >>> assignment_forms.render_batch_entry("CSCI251")  # Multiple assignments
    >>>
    >>> # Application settings forms
    >>> settings_forms = SettingsForms(controller)
    >>> settings_forms.render_grade_scale_config()  # Configure grading
    >>> settings_forms.render_import_export_settings()  # Data management
"""

from .assignment_forms import AssignmentForms
from .settings_forms import SettingsForms
from .subject_forms import SubjectForms

__all__ = [
    # Academic data forms - core entity management
    "SubjectForms",  # Subject creation, editing, and management forms
    "AssignmentForms",  # Assignment data entry and modification interfaces
    # Configuration forms - application settings
    "SettingsForms",  # Application preferences and configuration management
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Michael McMillan"
__description__ = "Form components for user input and data collection"

# Form capabilities summary
_FORM_CAPABILITIES = {
    "SubjectForms": {
        "domain": "Subject management and lifecycle operations",
        "forms": ["create", "edit", "delete_confirmation", "bulk_import"],
        "validation": ["subject_code_uniqueness", "name_format", "academic_standards"],
        "features": ["wizard_interface", "existing_data_population", "bulk_operations"],
    },
    "AssignmentForms": {
        "domain": "Assignment data entry and modification",
        "forms": ["create", "edit", "batch_entry", "delete_confirmation"],
        "validation": ["mark_ranges", "weight_percentages", "grade_types", "uniqueness"],
        "features": ["real_time_validation", "impact_analysis", "batch_processing"],
    },
    "SettingsForms": {
        "domain": "Application configuration and preferences",
        "forms": ["preferences", "grade_scale", "import_export", "theme_config"],
        "validation": ["setting_ranges", "file_paths", "format_validation"],
        "features": ["live_preview", "reset_defaults", "export_settings"],
    },
}

# Validation features
_VALIDATION_FEATURES = {
    "real_time": "Immediate feedback during user input",
    "business_rules": "Academic constraint enforcement",
    "cross_field": "Validation across related form fields",
    "error_recovery": "Clear guidance for error correction",
}

# User experience features
_UX_FEATURES = {
    "progressive_disclosure": "Complex forms broken into manageable steps",
    "auto_save": "Draft preservation during form completion",
    "contextual_help": "Inline guidance and validation messages",
    "accessibility": "Full keyboard navigation and screen reader support",
    "responsive_design": "Adaptive layouts for different screen sizes",
}
