from tkinter import END  # import END from tkinter
from ui import ToolTipManager


def update_treeview(app):
    """Update the treeview widget in the application."""
    semester_name = app.sheet_var.get()
    semester = app.semesters[semester_name]
    treeview_data = semester.sort_subjects()

    for row in app.treeview.get_children():
        app.treeview.delete(row)

    for row in treeview_data:
        app.treeview.insert("", "end", values=row)


def on_treeview_select(app, _event):
    """Update the subject code and derived subject name entries when a treeview row is selected."""
    selected_item = app.treeview.selection()
    if selected_item:
        selected_item_id = selected_item[0]
        values = app.treeview.item(selected_item_id, "values")
        if "Summary" in values[0] or "==" in values[0]:
            return

        subject_code = values[0]

        entries = [
            (app.subject_code_entry, subject_code),
            (app.subject_assessment_entry, values[2]),
            (app.weighted_mark_entry, values[4]),
            (app.mark_weight_entry, values[5].replace("%", ""))
        ]
        for entry, value in entries:
            entry.delete(0, END)
            entry.insert(0, value)


def on_treeview_motion(app, event):
    region = app.treeview.identify("region", event.x, event.y)
    if region == "cell":
        column = app.treeview.identify_column(event.x)
        row_id = app.treeview.identify_row(event.y)
        if column in ["#2", "#3"]:
            values = app.treeview.item(row_id, "values")
            if any("=" in val or "Assessments:" in val for val in values):
                return
            if len(values) > 1:
                text = values[int(column[1]) - 1]
                if app.current_tooltip:
                    app.current_tooltip.hide_tip(event)
                app.current_tooltip = ToolTipManager(app.treeview, text)
                app.current_tooltip.show_tip(event)
        else:
            if app.current_tooltip:
                app.current_tooltip.hide_tip(event)
                app.current_tooltip = None
    else:
        if app.current_tooltip:
            app.current_tooltip.hide_tip(event)
            app.current_tooltip = None


def on_window_resize(app, _event):
    """Update the treeview column width when the window is resized."""
    total_width = app.root.winfo_width()
    column_count = len(app.treeview["columns"])
    column_width = total_width // column_count
    for col in app.treeview["columns"]:
        app.treeview.column(col, width=column_width)
