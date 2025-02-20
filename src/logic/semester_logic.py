def update_semester(app, _event=None, *args):
    """Update the semester logic in the application."""
    selected_sheet = app.sheet_var.get()
    selected_year = app.year_var.get()
    if selected_sheet not in app.semesters:
        app.semesters[selected_sheet] = app.Semester(selected_sheet, selected_year, app.data_persistence)
    app.update_treeview()

def add_semester(app):
    """Adds a new semester to the application."""
    new_semester_name = app.simpledialog.askstring("Add Semester", "Enter the name of the new semester:")
    if new_semester_name:
        if new_semester_name in app.semesters:
            app.messagebox.showerror("Error", "Semester already exists!")
        else:
            app.semesters[new_semester_name] = app.Semester(new_semester_name, app.year_var.get(), app.data_persistence)
            app.semester_menu["menu"].add_command(
                label=new_semester_name,
                command=lambda value=new_semester_name: app.var.set(value)
            )
            app.sheet_var.set(new_semester_name)
            app.update_semester()

def remove_semester(app):
    """Removes the selected semester from the application."""
    semester_name = app.sheet_var.get()
    if semester_name:
        app.data_persistence.remove_semester(semester_name)
        app.update_semester()
        app.messagebox.showinfo("Success", f"Semester '{semester_name}' has been removed.")

def update_semester_menu(app):
    sheet_menu = app.semester_menu["menu"]
    sheet_menu.delete(0, "end")
    for semester_name in app.semesters:
        sheet_menu.add_command(label=semester_name, command=lambda value=semester_name: app.sheet_var.set(value))
    if app.semesters:
        app.sheet_var.set(list(app.semesters.keys())[0])
    else:
        app.sheet_var.set("")