from datetime import datetime
from tkinter import messagebox, ttk
import tkinter as tk
from data_persistence import DataPersistence
from semester import Semester


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

    def show_tip(self, event):
        if self.tip_window or not self.text:
            return
        x = event.x_root + 10
        y = event.y_root + 10
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="yellow", relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hide_tip(self, event):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class Application:
    def __init__(self, root: tk.Tk, data_persistence: DataPersistence):
        self.subject_code_entry = None
        self.subject_assessment_entry = None
        self.weighted_mark_entry = None
        self.mark_weight_entry = None
        self.total_mark_entry = None
        self.subject_assessment_label = None
        self.current_tooltip = None
        self.root = root

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        grid_frame = tk.Frame(main_frame)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.treeview = ttk.Treeview(grid_frame, columns=("Subject Code", "Subject Assessment", "Unweighted Mark",
                                                          "Weighted Mark", "Mark Weight", "Exam Mark", "Exam Weight"),
                                     show="headings")
        self.data_persistence = data_persistence
        self.semesters = {
            sem: Semester(sem, data_persistence.year, data_persistence)
            for sem in ["Autumn", "Spring", "Annual"]
        }

        current_year = datetime.now().year
        self.year_list = [str(year) for year in range(current_year - 2, current_year + 2, 1)]

        self.year_var = tk.StringVar()
        self.year_var.set(str(current_year))

        self.sheet_var = tk.StringVar()
        self.sheet_var.set("Autumn")

        self.setup_gui(grid_frame)

        self.root.bind("<Configure>", self.on_window_resize)

    def setup_gui(self, parent):
        sheet_label = tk.Label(parent, text="Select Sheet:")
        sheet_label.grid(row=0, column=0, padx=10, pady=10)

        sheet_menu = tk.OptionMenu(parent, self.sheet_var, "Autumn", "Spring", "Annual",
                                command=self.update_semester)
        sheet_menu.grid(row=0, column=1, padx=10, pady=10)

        year_label = tk.Label(parent, text="Select Year:")
        year_label.grid(row=1, column=0, padx=10, pady=10)

        year_menu = tk.OptionMenu(parent, self.year_var, *self.year_list, command=self.update_year)
        year_menu.grid(row=1, column=1, padx=10, pady=10)

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
            label = tk.Label(parent, text=f"{field}:")
            label.grid(row=row, column=0, padx=10, pady=10)
            setattr(self, attr, tk.Entry(parent, width=50))
            getattr(self, attr).grid(row=row, column=1, padx=10, pady=10)

        tk.Button(parent, text="Add Entry", command=self.add_entry).grid(row=6, column=0, columnspan=2, pady=10)
        tk.Button(parent, text="Delete Entry", command=self.delete_entry).grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(parent, text="Calculate Exam Mark", command=self.calculate_exam_mark).grid(row=8, column=0, columnspan=2, pady=10)

        tk.Button(parent, text="Sync All Semesters", command=self.sync_all_semesters).grid(row=9, column=0, columnspan=2, pady=10)

        self.treeview.grid(row=10, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.grid(row=10, column=2, sticky="ns", padx=(0, 10), pady=10)

        parent.grid_rowconfigure(10, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        self.treeview.bind("<Motion>", self.on_treeview_motion)
        self.treeview.bind("<<TreeviewSelect>>", self.on_treeview_select)

        self.update_semester()

    def on_treeview_select(self, event=None):
        selected_item = self.treeview.selection()
        if selected_item:
            selected_item_id = selected_item[0]
            values = self.treeview.item(selected_item_id, "values")

            entries = [
                (self.subject_code_entry, values[0]),
                (self.subject_assessment_entry, values[1]),
                (self.weighted_mark_entry, values[3]),
                (self.mark_weight_entry, values[4].replace("%", ""))
            ]

            for entry, value in entries:
                entry.delete(0, tk.END)
                entry.insert(0, value)

    def on_treeview_motion(self, event):
        region = self.treeview.identify("region", event.x, event.y)
        if region == "cell":
            column = self.treeview.identify_column(event.x)
            row_id = self.treeview.identify_row(event.y)

            if column == "#2":  # Assuming column index 2 is Subject Assessment
                values = self.treeview.item(row_id, "values")
                if len(values) > 1:
                    text = values[1]
                    if self.current_tooltip:
                        self.current_tooltip.hide_tip(event)
                    self.current_tooltip = ToolTip(self.treeview, text)
                    self.current_tooltip.show_tip(event)
            else:
                if self.current_tooltip:
                    self.current_tooltip.hide_tip(event)
                    self.current_tooltip = None
        else:
            if self.current_tooltip:
                self.current_tooltip.hide_tip(event)
                self.current_tooltip = None

    def on_window_resize(self, event=None):
        total_width = self.root.winfo_width()
        column_count = len(self.treeview["columns"])
        column_width = total_width // column_count
        for col in self.treeview["columns"]:
            self.treeview.column(col, width=column_width)

    def update_year(self, event=None):
        selected_year = self.year_var.get()
        self.data_persistence = DataPersistence(selected_year)
        self.semesters = {sem: Semester(sem, self.data_persistence.year, self.data_persistence) for sem in
                          self.semesters.keys()}
        self.update_semester()
        self.update_treeview()

    def update_semester(self, event=None):
        selected_sheet = self.sheet_var.get()
        selected_year = self.year_var.get()
        if self.semesters[selected_sheet] is None:
            self.semesters[selected_sheet] = Semester(selected_sheet, selected_year, self.data_persistence)
        self.update_treeview()

    def update_treeview(self):
        semester_name = self.sheet_var.get()
        semester = self.semesters[semester_name]
        treeview_data = semester.view_data()
        for row in self.treeview.get_children():
            self.treeview.delete(row)
        for row in treeview_data:
            self.treeview.insert("", "end", values=row)

    def add_entry(self):
        subject_code = self.subject_code_entry.get()
        subject_assessment = self.subject_assessment_entry.get()
        weighted_mark = self.weighted_mark_entry.get()
        mark_weight = self.mark_weight_entry.get()
        total_mark = self.total_mark_entry.get()
        semester_name = self.sheet_var.get()
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

    def delete_entry(self):
        selected_items = self.treeview.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select an item to delete.")
            return -1

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

    def sort_subjects(self, sort_by="Subject Code"):
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
            treeview_data.sort(key=lambda row: float(row[3]) if row[3] else 0)  # Sort by Weighted Mark
        elif sort_by == "Mark Weight":
            treeview_data.sort(key=lambda row: float(row[4].replace("%", "")) if row[4] else 0)  # Sort by Mark Weight

    

        # Optionally, display a success message
        messagebox.showinfo("Sorted", f"Subjects sorted by {sort_by}.")


    def calculate_exam_mark(self):
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

    def sync_all_semesters(self):
        combined_data = {
            "Autumn": self.data_persistence.data.get("Autumn", {}).copy(),
            "Spring": self.data_persistence.data.get("Spring", {}).copy(),
            "Annual": self.data_persistence.data.get("Annual", {}).copy()
        }

        # Add Annual data to Autumn and Spring for display purposes
        for subject, details in combined_data["Annual"].items():
            if subject not in combined_data["Autumn"]:
                combined_data["Autumn"][subject] = details
            if subject not in combined_data["Spring"]:
                combined_data["Spring"][subject] = details
        
        self.data_persistence.data = combined_data
        self.update_treeview()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    data_persistence = DataPersistence(str(datetime.now().year))
    app = Application(root, data_persistence)
    root.mainloop()
