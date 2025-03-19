from tkinter import messagebox


def add_entry(self):
    subject_code = self.subject_code_entry.get()
    semester_name = self.sheet_var.get()

    # Retrieve the stored subject name from the data structure
    subject_data = self.semesters[semester_name].data_persistence.data[semester_name].get(subject_code)
    if subject_data:
        subject_name = subject_data.get("Subject Name", "")
    else:
        messagebox.showerror("Error", "Subject code not found in data.")
        return
    subject_assessment = self.subject_assessment_entry.get()
    weighted_mark = self.weighted_mark_entry.get()
    mark_weight = self.mark_weight_entry.get()

    # Get the value of the sync source checkbox
    sync_source = self.sync_source_var.get()

    try:
        self.semesters[semester_name].add_entry(
            subject_code=subject_code,
            subject_name=subject_name,
            subject_assessment=subject_assessment,
            weighted_mark=weighted_mark,
            mark_weight=mark_weight,
            sync_source=sync_source,
        )
    except ValueError as error:
        messagebox.showerror("Error", f"Failed to add entry: {error}")
    self.update_treeview()


def delete_entry(self):
    selected_items = self.treeview.selection()
    if not selected_items:
        messagebox.showerror("Error", "Please select an item to delete.")
        return

    semester_name = self.sheet_var.get()
    semester = self.semesters[semester_name]
    for selected_item in selected_items:
        values = self.treeview.item(selected_item, "values")
        if len(values) < 2:
            continue

        subject_code = values[0]
        subject_assessment = values[2]

        # Remove the entry from the data structure
        if subject_code in semester.data_persistence.data[semester_name]:
            assessments = semester.data_persistence.data[semester_name][subject_code]["Assignments"]
            updated_assessments = [
                assessment for assessment in assessments if assessment["Subject Assessment"] != subject_assessment
            ]
            semester.data_persistence.data[semester_name][subject_code]["Assignments"] = updated_assessments

            # Remove the entry from the treeview
            self.treeview.delete(selected_item)

        # Save the updated data structure
        semester.data_persistence.save_data()

        # Parse 'Examinations' data
        try:
            mark_weight = float(self.mark_weight_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Mark Weight must be a valid number.")
            return

        # Fetch teh current exam weight
        current_exam_weight = float(
            semester.data_persistence.data[semester_name][subject_code]["Examinations"].get("Exam Weight", 0)
        )

        # Add the mark weight to the current exam weight
        exam_weight = current_exam_weight + mark_weight

        # Ensure the data structure for 'Examinations' exists before adding to it
        if "Examinations" not in semester.data_persistence.data[semester_name][subject_code]:
            semester.data_persistence.data[semester_name][subject_code]["Examinations"] = {}

        # Update only the "Exam Weight" field for the specific subject
        semester.data_persistence.data[semester_name][subject_code]["Examinations"]["Exam Weight"] = exam_weight

        messagebox.showinfo("Success", "Selected entry has been deleted.")

        # Save the updated data structure again
        semester.data_persistence.save_data()

    self.update_treeview()
