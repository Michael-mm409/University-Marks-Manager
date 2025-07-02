"""
University Marks Manager - Streamlit Application

This is the entry point for the University Marks Manager,
a Streamlit-based tool for managing and analyzing university subject marks.

It initializes the Model-View-Controller (MVC) structure by:
    - Configuring the Streamlit page settings
    - Creating the application controller (AppController)
    - Creating the main view (StreamlitView)
    - Rendering the application interface

Run this script directly to start the application.
"""

import streamlit as st

from controller.app_controller import AppController
from view import StreamlitView


def configure_page() -> None:
    """
    Configure Streamlit page settings.

    Sets:
        - Page title: "University Marks Manager"
        - Page icon: Custom icon from local `assets/` directory
        - Layout: Wide layout for better use of screen space
        - Sidebar state: Expanded by default
    """
    st.set_page_config(
        page_title="University Marks Manager",
        page_icon="assets/app_icon.ico",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main() -> None:
    """
    Main application entry point.

    Responsibilities:
        - Calls page configuration
        - Initializes the AppController (handles data & state)
        - Initializes the StreamlitView (handles UI rendering)
        - Renders the full user interface
    """
    configure_page()

    # Initialize MVC components
    controller = AppController()
    view = StreamlitView(controller)

    # Render the application
    view.render()


if __name__ == "__main__":
    main()
