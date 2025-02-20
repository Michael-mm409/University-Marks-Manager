"""
This module contains the Application class which is responsible for managing the 
user interface of the University Marks Manager application. It also includes the
ToolTip class for displaying tooltips when hovering over a Treeview cell.
"""
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk
import tkinter as tk
from data_persistence import DataPersistence
from ui import (configure_styles, create_main_frame,
                 create_form_frame, create_treeview,
                create_entry_frame, create_button_frames, ToolTipManager)
from semester import Semester
from typing import List, Dict, Any


class Application:
    """
    A class to represent the main application window for the University Marks Manager.
    This class is responsible for managing the user interface of the application,
    including adding, deleting, and calculating marks for subjects.
    
    Args:
        application_root (tk.Tk): The main application window.
        storage_handler (DataPersistence): An instance of the DataPersistence class.
    """
    def __init__(self, application_root: tk.Tk, storage_handler: DataPersistence):
        self.root = application_root
        self.data_persistence = storage_handler
        self.semesters = {
            sem: Semester(sem, storage_handler.year, storage_handler)
            for sem in self.data_persistence.data.keys()
        }

        current_year = datetime.now().year
        self.year_list = [str(year) for year in range(current_year - 2, current_year + 2, 1)]

        self.year_var = tk.StringVar()
        self.year_var.set(str(current_year))  # This sets the default year to current_year
        print(f"Current year in init: {datetime.now().year}")

        self.sheet_var = tk.StringVar()
        self.sheet_var.set("Autumn")

        # Initialise current tooltip to None
        self.current_tooltip = None
        print(current_year)

        self.setup_gui()

        self.root.bind("<Configure>", self.on_window_resize)

    def setup_gui(self):
        self.root.title("University Marks Manager")
        self.root.geometry("800x600")

        # 1. Configure styles
        configure_styles(self.root)
        
        # 2. Create main frame
        self.main_frame = create_main_frame(self.root)

        # 3. Create other frames
        create_form_frame(main_frame=self.main_frame, sheet_var=self.sheet_var,
                        year_var=self.year_var, semesters=self.semesters,
                        year_list= self.year_list, update_year=self.update_year,
                        update_semester=self.update_semester)
        
        self.treeview = create_treeview(self.main_frame)
        create_entry_frame(main_frame=self.main_frame, application_self=self)
        create_button_frames(main_frame=self.main_frame, application_self=self)

        # Bind events
        self.treeview.bind("<Motion>", self.on_treeview_motion)
        self.treeview.bind("<<TreeviewSelect>>", self.on_treeview_select)

        # Make the main frame expandable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Final step: update the semester
        self.update_semester()

    def on_treeview_select(self, _event=None):
        """
        Handles the selection event on the Treeview widget.
        
        Args:
            _event (tk.Event): The event that triggered the selection.
        """
        selected_item = self.treeview.selection()
        if selected_item:
            selected_item_id = selected_item[0]
            values = self.treeview.item(selected_item_id, "values")
            
            if "Summary" in values[0] or "==" in values[0]:
                return
                
            entries = [
                (self.subject_code_entry, values[0]),
                (self.subject_name_entry, values[1]),
                (self.subject_assessment_entry, values[2]),
                (self.weighted_mark_entry, values[4]),
                (self.mark_weight_entry, values[5].replace("%", ""))
            ]

            for entry, value in entries:
                entry.delete(0, tk.END)
                entry.insert(0, value)

    def on_treeview_motion(self, event):
        """
        Handles the mouse motion event on the Treeview widget.
        
        Args:
            event (tk.Event): The event that triggered the mouse motion.
        """
        region = self.treeview.identify("region", event.x, event.y)
        if (region == "cell"):
            column = self.treeview.identify_column(event.x)
            row_id = self.treeview.identify_row(event.y)

            if column in ["#2", "#3"]:  # Check if the column is Subject Name or Subject Assessment
                values = self.treeview.item(row_id, "values")

                if any("=" in value or "Assessments:" in value for value in values):
                    return
                if len(values) > 1:
                    text = values[int(column[1]) - 1]  # Get the text for the specific column
                    if self.current_tooltip:
                        self.current_tooltip.hide_tip(event)
                    self.current_tooltip = ToolTipManager(self.treeview, text)
                    self.current_tooltip.show_tip(event)
            else:
                if self.current_tooltip:
                    self.current_tooltip.hide_tip(event)
                    self.current_tooltip = None
        else:
            if self.current_tooltip:
                self.current_tooltip.hide_tip(event)
                self.current_tooltip = None

    def on_window_resize(self, _event=None):
        """
        Handles the window resize event and adjusts the column width of the Treeview widget.
        
        Args:
            event (tk.Event): The event that triggered the window resize.
        """
        total_width = self.root.winfo_width()
        column_count = len(self.treeview["columns"])
        column_width = total_width // column_count
        for col in self.treeview["columns"]:
            self.treeview.column(col, width=column_width)

    def update_year(self, _event=None):
        """
        Updates the year in the application.

        Args:
            event (tk.Event): The event that triggered the year update.
        """
        selected_year = self.year_var.get()
        self.data_persistence = DataPersistence(selected_year)
        self.semesters = {sem: Semester(sem, self.data_persistence.year, self.data_persistence)
                          for sem in self.semesters.keys()}
        self.update_semester()
        self.update_treeview()
        print(f"Year set in update_year: {selected_year}")

    def update_semester(self, _event=None, *args):
        """
        Updates the semester in the application.
        
        Args:
            event (tk.Event): The event that triggered the semester update.
        """
        selected_sheet = self.sheet_var.get()
        selected_year = self.year_var.get()
        if selected_sheet not in self.semesters:
            self.semesters[selected_sheet] = Semester(selected_sheet, selected_year, self.data_persistence)
        self.update_treeview()

    def update_treeview(self):
        """Updates the Treeview widget with the data from the selected semester."""
        semester_name = self.sheet_var.get()
        semester = self.semesters[semester_name]
        treeview_data = semester.sort_subjects()
        for row in self.treeview.get_children():
            self.treeview.delete(row)
        
        # print(f"Updating Treeview for Year: {self.year_var.get()} and Semester: {semester_name}")
        for row in treeview_data:
            # print(f"Inserting row: {row}")
            self.treeview.insert("", "end", values=row)

    def add_entry(self):
        """Adds a new entry to the selected semester with assignment details."""
        subject_code = self.subject_code_entry.get()
        subject_name = self.subject_name_entry.get()
        subject_assessment = self.subject_assessment_entry.get()
        weighted_mark = self.weighted_mark_entry.get()
        mark_weight = self.mark_weight_entry.get()
        total_mark = self.total_mark_entry.get()
        semester_name = self.sheet_var.get()

        # Get the value of the sync source checkbox
        sync_source = self.sync_source_var.get()

        try:
            self.semesters[semester_name].add_entry(
                semester=semester_name,
                subject_code=subject_code,
                subject_name=subject_name,
                subject_assessment=subject_assessment,
                weighted_mark=weighted_mark,
                mark_weight=mark_weight,
                total_mark=total_mark,
                sync_source=sync_source
            )
        except ValueError as error:
            messagebox.showerror("Error", f"Failed to add entry: {error}")
        self.update_treeview()

    def delete_entry(self):
        """
        Deletes the selected entry from the Treeview widget and the data structure.
        
        Returns:
            int: -1 if no item is selected, 0 if the item is deleted successfully.
        """
        selected_items = self.treeview.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select an item to delete.")
            return

        semester_name = self.sheet_var.get()
        semester = self.semesters[semester_name]
        for selected_item in selected_items:
            values = self.treeview.item(selected_item, "values")
            if len(values) < 2:
                continue  # Skip if values are not sufficient

            subject_code = values[0]
            subject_assessment = values[1]

            # Remove the entry from the data structure
            if subject_code in semester.data_persistence.data[semester_name]:
                assessments = semester.data_persistence.data[semester_name][subject_code]["Assignments"]
                updated_assessments = [assessment for assessment in assessments if
                                       assessment["Subject Assessment"] != subject_assessment]

                semester.data_persistence.data[semester_name][subject_code]["Assignments"] = updated_assessments

                # Remove the entry from the tree view
                self.treeview.delete(selected_item)

            # Save the updated data structure
            semester.data_persistence.save_data()

            # Parse 'Examinations'
            try:
                mark_weight = float(self.mark_weight_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Mark Weight must be a valid number.")
                return

            # Fetch the current exam weight
            current_exam_weight = float(
                semester.data_persistence.data[semester_name][subject_code]["Examinations"].get("Exam Weight", 0))

            # Add the mark weight to the current exam weight
            exam_weight = current_exam_weight + mark_weight

            # Print statements for debugging
            print(f"Current Exam Weight for {subject_code}: {current_exam_weight}")
            print(f"Added Mark Weight: {mark_weight}")
            print(f"New Calculated Exam Weight for {subject_code}: {exam_weight}")

            # Ensure the data structure for 'Examinations' exists before adding to it
            if "Examinations" not in semester.data_persistence.data[semester_name][subject_code]:
                semester.data_persistence.data[semester_name][subject_code]["Examinations"] = {}

            # Update only the "Exam Weight" field for the specific subject
            semester.data_persistence.data[semester_name][subject_code]["Examinations"]["Exam Weight"] = exam_weight

            messagebox.showinfo("Success", "Selected entry has been deleted.")

            # Save the updated data structure again
            semester.data_persistence.save_data()

        self.update_treeview()

    def add_semester(self):
        """Add a new semester to the application."""
        new_semester_name = simpledialog.askstring("Add Semester", "Enter the name of the new semester:")
        if new_semester_name:
            if new_semester_name in self.semesters:
                messagebox.showerror("Error", "Semester already exists!")
            else:
                self.semesters[new_semester_name] = Semester(new_semester_name, self.year_var.get(), self.data_persistence)
                self.semester_menu["menu"].add_command(label=new_semester_name, command=tk._setit(self.sheet_var, new_semester_name, self.update_semester))
                self.sheet_var.set(new_semester_name)
                self.update_semester()

    def remove_semester(self):
        """Removes an existing semester from the data structure."""
        semester_name = simpledialog.askstring("Remove Semester", "Enter the name of the semester:")
        if semester_name:
            self.data_persistence.remove_semester(semester_name)
            self.update_semester_menu()
            messagebox.showinfo("Success", f"Semester '{semester_name}' removed successfully.")

    def update_semester_menu(self):
        """Updates the semester menu with the latest semesters."""
        sheet_menu = self.semester_menu["menu"]
        sheet_menu.delete(0, "end")
        for semester in self.semesters.keys():
            sheet_menu.add_command(label=semester, command=lambda value=semester: self.sheet_var.set(value))
        if self.semesters:
            self.sheet_var.set(list(self.semesters.keys())[0])
        else:
            self.sheet_var.set("")
    
    def sort_subjects(self, sort_by="Subject Code"):
        """
        Sorts the subjects in the Treeview widget based on the selected field.
        
        Args:
            sort_by (str, optional):
                The field by which the subjects are sorted. Defaults to "Subject Code".
        """
        semester_name = self.sheet_var.get()
        semester = self.semesters[semester_name]
        semester.sort_subjects(sort_by)
        # Get the data to be sorted
        treeview_data = semester.view_data()

        # Sort by the chosen field (Subject Code, Subject Assessment, Weighted Mark, Mark Weight)
        if sort_by == "Subject Code":
            treeview_data.sort(key=lambda row: row[0])  # Sort by Subject Code
        elif sort_by == "Subject Assessment":
            treeview_data.sort(key=lambda row: row[1])  # Sort by Subject Assessment
        elif sort_by == "Weighted Mark":
            treeview_data.sort(key=lambda row:
                               float(row[3]) if row[3] else 0)  # Sort by Weighted Mark
        elif sort_by == "Mark Weight":
            treeview_data.sort(key=lambda row:
                               float(row[4].replace("%", ""))
                               if row[4] else 0)  # Sort by Mark Weight

        # Optionally, display a success message
        messagebox.showinfo("Sorted", f"Subjects sorted by {sort_by}.")


    def calculate_exam_mark(self):
        """Synchronises all semesters' data into a single data structure."""
        semester_name = self.sheet_var.get()
        subject_code = self.subject_code_entry.get()
        if not subject_code:
            messagebox.showerror("Error", "Please enter a Subject Code.")
            return
        exam_mark = self.semesters[semester_name].calculate_exam_mark(subject_code)

        self.update_treeview()
        if exam_mark is not None:
            messagebox.showinfo("Success", f"Exam Mark for {subject_code}: {exam_mark}")
        else:
            messagebox.showerror("Error", f"Subject {subject_code} not found.")
            self.update_treeview()

    def add_subject(self):
        """Add a new subject to the selected semester."""
        subject_code = simpledialog.askstring("Add Subject", "Enter the subject code:")
        subject_name = simpledialog.askstring("Add Subject", "Enter the subject name:")
        sync_source = messagebox.askyesno("Sync Subject", "Should this subject be a sync source?")

        if subject_code and subject_name:
            semester_name = self.sheet_var.get()
            self.semesters[semester_name].add_subject(subject_code, subject_name, sync_source)
            self.update_treeview()

    def remove_subject(self):
        """Remove a subject from the selected semester."""
        subject_code = simpledialog.askstring("Remove Subject", "Enter the subject code to remove:")

        if subject_code:
            semester_name = self.sheet_var.get()
            self.semesters[semester_name].remove_subject(subject_code)
            self.update_treeview()