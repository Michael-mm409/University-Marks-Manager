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

from tkinter import Tk

from model.persistence.data_persistence import DataPersistence
from view import ask_semesters
from model import Application


def main():
    root = Tk()

    year = datetime.now().year
    icon_path = "./assets/app_icon.ico"  # Optional icon path

    # Ask the user for semesters if the data file does not exist
    file_path = f"./data/{year}.json"
    if not path.exists(file_path):
        selected_semesters = ask_semesters(root, icon_path)
        if not selected_semesters:
            print("No semesters selected. Exiting.")
            return
    else:
        selected_semesters = None  # Use existing data

    # Initialize DataPersistence with the selected semesters
    data_persistence = DataPersistence(year, semesters=selected_semesters)
    Application(root, data_persistence, icon_path)
    print(f"Initialized data for year {year}: {data_persistence.data}")

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Exiting application.")
        root.destroy()


if __name__ == "__main__":
    main()
