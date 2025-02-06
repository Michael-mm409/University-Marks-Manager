"""University Marks Manager Application

This script initializes the GUI application for managing university marks.
It sets up the main application window, initializes data persistence, and
runs the Tkinter event loop.

Modules:
    tkinter (tk): Provides GUI components.
    datetime (datetime): Handles date-related operations.
    application (Application): Main application logic.
    data_persistence (DataPersistence): Handles data storage and retrieval.

Usage:
    Run this script to launch the University Marks Manager.
"""

import tkinter as tk
from datetime import datetime
from application import Application
from data_persistence import DataPersistence

if __name__ == "__main__":
    root = tk.Tk()

    # Enable window resizing (set both width and height to True)
    root.resizable(width=True, height=True)

    root.title("University Marks Manager")
    data_persistence = DataPersistence(
        str(datetime.now().year))  # Year is set as 2024 for demonstration
    app = Application(root, data_persistence)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()
