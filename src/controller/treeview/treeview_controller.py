from tkinter import END
from typing import Any, List, Tuple

from view import ToolTipManager


def __update_entry_fields(entries: List[Tuple[Any, str]]) -> None:
    """
    Update the given entry fields with the provided values.

    Args:
        entries (List[Tuple[Any, str]]): A list of tuples containing entry widgets and their corresponding values.
    """
    for entry, value in entries:
        entry.delete(0, END)
        entry.insert(0, value)


def on_treeview_select(self, _event) -> None:
    """
    Update the subject code and derived subject name entries when a treeview row is selected.

    Args:
        _event: The event that triggered the selection.
    """
    selected_item = self.treeview.selection()
    if selected_item:
        selected_item_id = selected_item[0]
        values = list(self.treeview.item(selected_item_id, "values"))

        # Skip rows with "Summary" or "==" in the first column
        if "Summary" in values[0] or "==" in values[0]:
            return

        # Handle rows with "No assignments available"
        if "No assignments available" in values[2]:
            values[2] = ""

        subject_code = values[0]

        # Define the entries to update
        entries = [
            (self.subject_code_entry, subject_code),
            (self.subject_assessment_entry, values[2]),
            (self.weighted_mark_entry, values[4]),
            (self.mark_weight_entry, values[5].replace("%", "")),
        ]

        # Update the entry fields
        __update_entry_fields(entries)


def on_treeview_motion(self, event) -> None:
    """
    Display a tooltip when hovering over specific treeview cells.

    Args:
        event: The motion event triggered by the mouse movement.
    """
    region = self.treeview.identify("region", event.x, event.y)
    if region == "cell":
        column = self.treeview.identify_column(event.x)
        row_id = self.treeview.identify_row(event.y)
        values = self.treeview.item(row_id, "values")

        # Show tooltip for specific columns and valid rows
        if column in ("#2", "#3") and values[2] != "No assignments available":
            if any("=" in val or "Assessments:" in val for val in values):
                if self.current_tooltip:
                    self.current_tooltip.hide_tip(event)
                return

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


def on_window_resize(self, _event) -> None:
    """
    Update the treeview column width when the window is resized.

    Args:
        _event: The event that triggered the resize.
    """
    total_width = self.root.winfo_width()
    column_count = len(self.treeview["columns"])
    column_width = total_width // column_count

    for col in self.treeview["columns"]:
        self.treeview.column(col, width=column_width)
