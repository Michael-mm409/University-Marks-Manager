import datetime
from tkinter import messagebox, ttk
import tkinter as tk

from data_persistence import DataPersistence
from semester import Semester


class Application:
    def __init__(self, root: tk.Tk, data_persistence: DataPersistence):
        self.root = root

        # Treeview for viewing data in a table-like format
        self.treeview = ttk.Treeview(self.root, columns=("Subject Code", "Subject Assessment", "Unweighted Mark",
                                                         "Weighted Mark", "Mark Weight", "Exam Mark", "Exam Weight"),
                                     show="headings")
        self.data_persistence = data_persistence
        self.semesters = {
            sem: Semester(sem, data_persistence.year, data_persistence)
            for sem in ["Autumn", "Spring", "Annual"]
        }

        # Get the current year
        current_year = datetime.datetime.now().year

        # Create the list of years for the dropdown (current year and next two years)
        self.year_list = [str(year) for year in range(current_year-2,current_year + 2, 1)]

        # Set the default year to the current year
        self.year_var = tk.StringVar()
        self.year_var.set(str(current_year))  # Default value to the current year

        self.sheet_var = tk.StringVar()
        self.sheet_var.set("Autumn")  # Default semester to Autumn

        self.setup_gui()

        # Bind the resizing event to adjust column widths
        self.root.bind("<Configure>", self.on_window_resize)

    def setup_gui(self):
        """Setup the main GUI elements."""
        # Sheet selection (e.g., Autumn, Spring, Annual)
        sheet_label = tk.Label(self.root, text="Select Sheet:")
        sheet_label.grid(row=0, column=0, padx=10, pady=10)

        sheet_menu = tk.OptionMenu(self.root, self.sheet_var, "Autumn", "Spring", "Annual",
                                   command=self.update_semester)
        sheet_menu.grid(row=0, column=1, padx=10, pady=10)

        # Year selection (e.g., 2024, 2025, etc.)
        year_label = tk.Label(self.root, text="Select Year:")
        year_label.grid(row=1, column=0, padx=10, pady=10)

        year_menu = tk.OptionMenu(self.root, self.year_var, *self.year_list, command=self.update_year)
        year_menu.grid(row=1, column=1, padx=10, pady=10)

        # Define the columns for the treeview with descriptive headings
        headings = {
            "Subject Code": "Subject Code",
            "Subject Assessment": "Subject Assessment",
            "Unweighted Mark": "Mark (Out of Full Score)",
            "Weighted Mark": "Weighted Contribution (%)",
            "Mark Weight": "Assessment Weight (e.g., 30%)",
            "Exam Mark": "Exam Mark (Calculated)",
            "Exam Weight": "Exam Weight (%)",
        }

        for col, description in headings.items():
            self.treeview.heading(col, text=description)
            self.treeview.column(col, anchor=tk.CENTER)

        fields = [
            ("Subject Code", 2, "subject_code_entry"),
            ("Subject Assessment", 3, "subject_assessment_entry"),
            ("Weighted Mark", 4, "weighted_mark_entry"),
            ("Mark Weight", 5, "mark_weight_entry"),
            ("Total Mark", 6, "total_mark_entry"),
        ]

        for field, row, attr in fields:
            tk.Label(self.root, text=f"{field}:").grid(row=row, column=0, padx=10, pady=10)
            setattr(self, attr, tk.Entry(self.root))
            getattr(self, attr).grid(row=row, column=1, padx=10, pady=10)

        # Button to add entry
        tk.Button(self.root, text="Add Entry", command=self.add_entry).grid(row=6, column=0, columnspan=2, pady=10)
        # Button to calculate final mark
        calculate_button = tk.Button(self.root, text="Calculate Exam Mark", command=self.calculate_exam_mark)
        calculate_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Button to sync semesters
        sync_button = tk.Button(self.root, text="Sync All Semesters", command=self.sync_all_semesters)
        sync_button.grid(row=8, column=0, columnspan=2, pady=10)

        # Configure the TreeView
        self.treeview.grid(row=9, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Add a scrollbar for the Treeview
        v_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.grid(row=9, column=2, sticky="ns", padx=(0, 10), pady=10)

        # Configure grid weights to make the TreeView resizable
        self.root.grid_rowconfigure(9, weight=1)
        self.root.grid_rowconfigure(10, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Update the semester
        self.update_semester()

    def on_window_resize(self, event=None):
        """Automatically adjust column widths on window resize."""
        total_width = self.root.winfo_width()
        column_count = len(self.treeview["columns"])

        # Set the width of each column to be proportional to the total window width
        column_width = total_width // column_count
        for col in self.treeview["columns"]:
            self.treeview.column(col, width=column_width)

    def update_year(self, event=None):
        """Update the year based on the selection from the dropdown."""
        selected_year = self.year_var.get()

        # Reinitialize DataPersistence with the selected year
        self.data_persistence = DataPersistence(selected_year)

        self.semesters = {sem: Semester(sem, self.data_persistence.year, self.data_persistence) for sem in
                          self.semesters.keys()}

        self.update_semester()
        self.update_treeview()

    def update_semester(self, event=None):
        """Update the semester data based on the selected sheet and year."""
        selected_sheet = self.sheet_var.get()
        selected_year = self.year_var.get()

        # Ensure the semester is properly initialized
        if self.semesters[selected_sheet] is None:
            self.semesters[selected_sheet] = Semester(selected_sheet, selected_year, self.data_persistence)

        self.update_treeview()

    def update_treeview(self):
        """Update the TreeView widget with data from the selected semester."""
        semester_name = self.sheet_var.get()  # Get the current semester
        semester = self.semesters[semester_name]  # Retrieve the Semester
        treeview_data = semester.view_data()  # Get the data for TreeView

        # Clear the TreeView
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        # Insert data into the TreeView
        for row in treeview_data:
            self.treeview.insert("", "end", values=row)


    def add_entry(self):
        """Method to add an entry in the selected semester."""
        subject_code = self.subject_code_entry.get()
        subject_assessment = self.subject_assessment_entry.get()
        weighted_mark = self.weighted_mark_entry.get()
        mark_weight = self.mark_weight_entry.get()
        total_mark = self.total_mark_entry.get()

        semester_name = self.sheet_var.get()

        # Add entry using the Semester
        try:
            self.semesters[semester_name].add_entry(
                semester=semester_name,
                subject_code=subject_code,
                subject_assessment=subject_assessment,
                weighted_mark=weighted_mark,
                mark_weight=mark_weight,
                total_mark=total_mark
            )
        except Exception as error:
            messagebox.showerror("Error", f"Failed to add entry: {error}")

        self.update_treeview()

    def calculate_exam_mark(self):
        """Calculate the exam mark for the selected semester's subject."""
        semester_name = self.sheet_var.get()
        subject_code = self.subject_code_entry.get()
        if not subject_code:
            messagebox.showerror("Error", "Please enter a Subject Code.")
            return

        exam_mark = self.semesters[semester_name].calculate_exam_mark(subject_code)
        if exam_mark is not None:
            messagebox.showinfo("Success", f"Exam Mark for {subject_code}: {exam_mark}")
        else:
            messagebox.showerror("Error", f"Subject {subject_code} not found.")
        self.update_treeview()

    def sync_all_semesters(self):
        """Sync data for all semesters"""
        self.data_persistence.sync_semesters()
        self.update_treeview()
