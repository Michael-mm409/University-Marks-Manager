def add_entry(app):
    subject_code = app.subject_code_entry.get()
    subject_name = app.subject_name_entry.get()
    subject_assessment = app.subject_assessment_entry.get()
    weighted_mark = app.weighted_mark_entry.get()
    mark_weight = app.mark_weight_entry.get()
    total_mark = app.total_mark_entry.get()
    semester_name = app.sheet_var.get()

    # Get the value of the sync source checkbox
    sync_source = app.sync_source_var.get()

    try:
        app.semesters[semester_name].add_entry(
            subject_code=subject_code,
            subject_name=subject_name,
            subject_assessment=subject_assessment,
            weighted_mark=weighted_mark,
            mark_weight=mark_weight,
            total_mark=total_mark,
            sync_source=sync_source
        )
    except ValueError as error:
        app.messagebox.showerror("Error", f"Failed to add entry: {error}")
    app.update_treeview()

def delete_entry(app):
    selected_items = app.treeview.selection()
    if not selected_items:
        app.messagebox.showerror("Error", "Please select an item to delete.")
        return

    semester_name = app.sheet_var.get()
    semester = app.semesters[semester_name]
    for selected_item in selected_items:
        values = app.treeview.item(selected_item, "values")
        if len(values) < 2:
            continue

        subject_code = values[0]
        subject_assessment = values[1]

        # Remove the entry from the data structure
        if subject_code in semester.data_persistence.data[semester_name]:
            assessments = semester.data_persistence.data[semester_name][subject_code]["Assignments"]
            updated_assessments = [
                assessment for assessment in assessments
                if assessment["Subject Assessment"] != subject_assessment
            ]
            semester.data_persistence.data[semester_name][subject_code]["Assignments"] = updated_assessments

            # Remove the entry from the treeview
            app.treeview.delete(selected_item)

        # Save the updated data structure
        semester.data_persistence.save_data()

        # Parse 'Examinations' data
        try:
            mark_weight = float(app.mark_weight_entry.get())
        except ValueError:
            app.messagebox.showerror("Error", "Mark Weight must be a valid number.")
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

        app.messagebox.showinfo("Success", "Selected entry has been deleted.")

        # Save the updated data structure again
        semester.data_persistence.save_data()

    app.update_treeview()