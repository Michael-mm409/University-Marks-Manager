from tkinter import END

from view import ToolTipManager


def on_treeview_select(self, _event):
    """Update the subject code and derived subject name entries when a treeview row is selected."""
    selected_item = self.treeview.selection()
    if selected_item:
        selected_item_id = selected_item[0]
        values = list(self.treeview.item(selected_item_id, "values"))
        if "Summary" in values[0] or "==" in values[0]:
            return

        if "No assignments available" in values[2]:
            values[2] = ""

        subject_code = values[0]

        entries = [
            (self.subject_code_entry, subject_code),
            (self.subject_assessment_entry, values[2]),
            (self.weighted_mark_entry, values[4]),
            (self.mark_weight_entry, values[5].replace("%", "")),
        ]
        for entry, value in entries:
            entry.delete(0, END)
            entry.insert(0, value)


def on_treeview_motion(self, event):
    region = self.treeview.identify("region", event.x, event.y)
    if region == "cell":
        column = self.treeview.identify_column(event.x)
        row_id = self.treeview.identify_row(event.y)
        values = self.treeview.item(row_id, "values")
        if column == "#2" or (column == "#3" and values[2] != "No assignments available"):
            if any("=" in val or "Assessments:" in val for val in values):
                if self.current_tooltip:
                    self.current_tooltip.hide_tip(event)
                return
            # if len(values) > 1:
            text = values[int(column[1]) - 1]
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


def on_window_resize(self, _event):
    """Update the treeview column width when the window is resized."""
    total_width = self.root.winfo_width()
    column_count = len(self.treeview["columns"])
    column_width = total_width // column_count
    for col in self.treeview["columns"]:
        self.treeview.column(col, width=column_width)
