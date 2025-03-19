"""University Marks Manager Application

This script initializes the GUI application for managing university marks.
It sets up the main application window, initializes data persistence, and
runs the Tkinter event loop.

Modules:
    tkinter (tk): Provides GUI components.
    customtkinter (ctk): Custom-themed Tkinter components.
    datetime (datetime): Handles date-related operations.
    application (Application): Main application logic.
    data_persistence (DataPersistence): Handles data storage and retrieval.

Usage:
    Run this script to launch the University Marks Manager.
"""

from datetime import datetime
from os import path

import customtkinter as ctk

from model import Application, DataPersistence


def main():
    # Optionally, set the appearance mode and color theme
    ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Options: "blue", "dark-blue", "green"

    icon_path = path.abspath(r"assets\app_icon.ico")  # Use the .ico file

    # Create the main application window
    root = ctk.CTk()
    root.title("University Marks Manager")
    root.resizable(width=True, height=True)

    # Set the icon for the main window
    try:
        root.iconbitmap(default=icon_path)
        print("Icon set for the main window.")
    except Exception as e:
        print(f"Failed to set icon: {e}")

    data_persistence = DataPersistence(str(datetime.now().year))

    Application(root, data_persistence, icon_path)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()


if __name__ == "__main__":
    main()
