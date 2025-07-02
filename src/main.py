"""
University Marks Manager - Streamlit Application
Entry point for the Streamlit-based university marks management system.
"""

import streamlit as st

from controller.app_controller import AppController
from view.streamlit_views import StreamlitView


def configure_page() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="University Marks Manager",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main() -> None:
    """Main application entry point."""
    configure_page()

    # Initialize MVC components
    controller = AppController()
    view = StreamlitView(controller)

    # Render the application
    view.render()


if __name__ == "__main__":
    main()
