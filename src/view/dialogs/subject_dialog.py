from tkinter import messagebox

import customtkinter as ctk

from .base_dialog import BaseDialog


class AddSubjectDialog(BaseDialog):
    def body(self, master):
        button_frame = super().body(master)  # Call the base class body method and get the button frame

        # Add custom UI elements for AddSubjectDialog
        ctk.CTkLabel(button_frame, text="Subject Code:", fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w", padx=10, pady=5
        )
        self.entry_code = ctk.CTkEntry(button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_code.pack(fill="x", padx=10)

        ctk.CTkLabel(button_frame, text="Subject Name:", fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w", padx=10, pady=5
        )
        self.entry_name = ctk.CTkEntry(button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_name.pack(fill="x", padx=10)

        # Add sync source checkbox
        self.sync_source_var = ctk.BooleanVar()
        ctk.CTkCheckBox(button_frame, text="Sync Subject Across All Semesters", variable=self.sync_source_var).pack(
            side="top", anchor="w", padx=10, pady=5
        )

        return self.entry_code  # Set initial focus

    def apply(self):
        subject_code = self.entry_code.get().strip()
        subject_name = self.entry_name.get().strip()
        sync_source = self.sync_source_var.get()

        if not subject_code or not subject_name:
            messagebox.showerror("Error", "Subject Code and Subject Name cannot be empty.")
            self.result = None
        else:
            self.result = {
                "subject_code": subject_code,
                "subject_name": subject_name,
                "sync_source": sync_source,
            }


class AddTotalMarkDialog(BaseDialog):
    def body(self, master):
        """Create the dialog body."""
        self.label = ctk.CTkLabel(master, text="Enter the total mark (0-100):")
        self.label.pack(pady=10)

        self.entry = ctk.CTkEntry(master)
        self.entry.pack(pady=10)

        return self.entry  # Set focus to the entry widget

    def apply(self):
        """Retrieve the total mark entered by the user."""
        try:
            self.result = float(self.entry.get())
        except ValueError:
            self.result = None


class RemoveSubjectDialog(BaseDialog):
    def __init__(self, parent, title=None, message=None, icon_path=None, geometry="250x150"):
        self.message = message
        super().__init__(parent, title=title, icon_path=icon_path, geometry=geometry)

    def body(self, master):
        super().body(master)  # Call the base class body method

        # Add custom UI elements for RemoveSubjectDialog
        ctk.CTkLabel(self.button_frame, text=self.message, fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w", padx=10, pady=5
        )
        self.entry_code = ctk.CTkEntry(self.button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_code.pack(fill="x", padx=10)

        return self.entry_code  # Set initial focus

    def apply(self):
        self.result = self.entry_code.get().strip() or None


def ask_remove_subject(parent, title=None, message=None, icon_path=None):
    """Creates the remove subject dialog and returns the input value."""
    dialog = RemoveSubjectDialog(parent=parent, title=title, message=message, icon_path=icon_path)
    return dialog.result


def ask_add_subject(parent, title=None, message=None, icon_path=None):
    """
    Display a dialog to add a subject.

    Args:
        parent: The parent window.
        title: The title of the dialog.
        message: The message to display in the dialog.
        icon_path: The path to the icon file.

    Returns:
        Tuple[str, str, bool]: The subject code, subject name, and sync source.
    """
    dialog = AddSubjectDialog(parent, title, icon_path=icon_path, geometry="250x200")
    if dialog.result is None:
        return None, None, None  # Handle case where dialog is canceled or invalid input
    return dialog.result["subject_code"], dialog.result["subject_name"], dialog.result["sync_source"]


def ask_add_total_mark(parent, title=None, message=None, icon_path=None):
    """
    Display a dialog to ask the user for the total mark.

    Args:
        parent: The parent window.
        title: The title of the dialog.
        message: The message to display in the dialog.
        icon_path: The path to the icon file.

    Returns:
        float: The total mark entered by the user, or None if canceled.
    """
    dialog = AddTotalMarkDialog(parent, title=title, icon_path=icon_path, geometry="300x150")
    return dialog.result
