"""University Marks Manager Application

This script initializes the GUI application for managing university marks.
It sets up the main application window, initializes data persistence, and
runs the Tkinter event loop.

Modules:
    PyQt6.QtWidgets (QApplication, QMainWindow): Provides GUI Components.
    datetime (datetime): Handles date-related operations.
    application (Application): Main application logic.
    data_persistence (DataPersistence): Handles data storage and retrieval.

Usage:
    Run this script to launch the University Marks Manager.
"""

import sys
from datetime import datetime

from PyQt6.QtWidgets import QApplication

from application.main_window import Application
from data_persistence import DataPersistence

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialise data persistence with the current year
    data_persistence = DataPersistence(str(datetime.now().year))

    # Create and show the main window
    window = Application(data_persistence)  # Ensure Application inherits from QMainWindow or QWidget
    window.show()

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("Application closed.")
