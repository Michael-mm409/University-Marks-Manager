"""
This module contains the Application class which is responsible for managing the
user interface of the University Marks Manager application. It also includes the
ToolTip class for displaying tooltips when hovering over a Treeview cell.
"""
from datetime import datetime
import customtkinter as tk
from data_persistence import DataPersistence
from semester import Semester
from ui import (configure_styles, create_main_frame,
                create_form_frame, create_treeview,
                create_entry_frame, create_button_frames)
from application_logic import (
    update_year, update_semester, add_semester, remove_semester, update_semester_menu,
    add_subject, remove_subject, add_entry, delete_entry, calculate_exam_mark,
    update_treeview, on_treeview_select, on_treeview_motion, on_window_resize
)


class Application:
    """
    A class to represent the main application window for the University Marks Manager.
    This class is responsible for managing the user interface of the application,
    including adding, deleting, and calculating marks for subjects.

    Args:
        application_root (tk.Tk): The main application window.
        storage_handler (DataPersistence): An instance of the DataPersistence class.
    """
    def __init__(self, application_root: tk.CTk, storage_handler: DataPersistence):
        self.root = application_root
        self.data_persistence = storage_handler
        self.semesters = {
            sem: Semester(sem, storage_handler.year, storage_handler)
            for sem in self.data_persistence.data.keys()
        }
        current_year = datetime.now().year
        self.year_list = [str(year) for year in range(current_year - 2, current_year + 2, 1)]
        self.year_var = tk.StringVar()
        self.year_var.set(str(current_year))
        self.sheet_var = tk.StringVar()
        self.sheet_var.set("Autumn")
        self.sync_source_var = tk.BooleanVar()
        self.current_tooltip = None

        self.setup_gui()
        self.root.bind("<Configure>", self.on_window_resize)

    def setup_gui(self):
        self.root.title("University Marks Manager")
        self.root.geometry("1850x800")
        configure_styles(self.root)
        self.main_frame = create_main_frame(self.root)
        self.create_form_frame()
        self.create_treeview()
        self.create_entry_frame()
        self.create_button_frames()
        self.bind_events()
        self.configure_grid()
        self.update_semester()

    def create_form_frame(self):
        create_form_frame(main_frame=self.main_frame,
                          sheet_var=self.sheet_var,
                          year_var=self.year_var,
                          semesters=self.semesters,
                          year_list=self.year_list,
                          update_year=self.update_year,
                          update_semester=self.update_semester)

    def create_treeview(self):
        self.treeview = create_treeview(self.main_frame)

    def create_entry_frame(self):
        create_entry_frame(main_frame=self.main_frame, application_self=self)

    def create_button_frames(self):
        create_button_frames(main_frame=self.main_frame, application_self=self)

    def bind_events(self):
        self.treeview.bind("<Motion>", lambda event: on_treeview_motion(self, event))
        self.treeview.bind("<<TreeviewSelect>>", lambda event: on_treeview_select(self, event))

    def configure_grid(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def update_year(self, event=None):
        update_year(self, event)

    def update_semester(self, event=None):
        update_semester(self, event)

    def add_semester(self):
        add_semester(self)

    def remove_semester(self):
        remove_semester(self)

    def update_semester_menu(self):
        update_semester_menu(self)

    def add_subject(self):
        add_subject(self)

    def remove_subject(self):
        remove_subject(self)

    def add_entry(self):
        add_entry(self)

    def delete_entry(self):
        delete_entry(self)

    def calculate_exam_mark(self):
        calculate_exam_mark(self)

    def update_treeview(self):
        update_treeview(self)

    def on_treeview_select(self, event):
        on_treeview_select(self, event)

    def on_treeview_motion(self, event):
        on_treeview_motion(self, event)

    def on_window_resize(self, event):
        on_window_resize(self, event)
