from tkinter import messagebox

import customtkinter as ctk

from .base_dialog import BaseDialog


class AddSubjectDialog(BaseDialog):
    def body(self, master):
        super().body(master)  # Call the base class body method

        # Add custom UI elements for AddSubjectDialog
        ctk.CTkLabel(self.button_frame, text="Subject Code:", fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w", padx=10, pady=5
        )
        self.entry_code = ctk.CTkEntry(self.button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_code.pack(fill="x", padx=10)

        ctk.CTkLabel(self.button_frame, text="Subject Name:", fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w", padx=10, pady=5
        )
        self.entry_name = ctk.CTkEntry(self.button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_name.pack(fill="x", padx=10)

        # Add sync source checkbox
        self.sync_source_var = ctk.BooleanVar()
        ctk.CTkCheckBox(
            self.button_frame, text="Sync Subject Across All Semesters", variable=self.sync_source_var
        ).pack(side="top", anchor="w", padx=10, pady=5)

        return self.entry_code  # Set initial focus

    def apply(self):
        self.result = {
            "subject_code": self.entry_code.get().strip() or None,
            "subject_name": self.entry_name.get().strip() or None,
            "sync_source": self.sync_source_var.get(),
        }


class AddTotalMarkDialog(BaseDialog):
    def body(self, master):
        super().body(master)  # Call the base class body method

        # Add custom UI elements for AddTotalMarkDialog
        ctk.CTkLabel(self.button_frame, text="Enter Total Mark:", fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w", padx=10
        )
        self.entry_total_mark = ctk.CTkEntry(self.button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_total_mark.pack(fill="x", padx=10)

        return self.entry_total_mark  # Set initial focus

    def apply(self):
        value = self.entry_total_mark.get().strip()
        try:
            self.result = float(value) if value else None
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid number.")
            self.result = None


class RemoveSubjectDialog(BaseDialog):
    def body(self, master):
        super().body(master)  # Call the base class body method

        # Add custom UI elements for RemoveSubjectDialog
        ctk.CTkLabel(self.button_frame, text="Subject Code:", fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w", padx=10, pady=5
        )
        self.entry_code = ctk.CTkEntry(self.button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_code.pack(fill="x", padx=10)

        return self.entry_code  # Set initial focus

    def apply(self):
        self.result = self.entry_code.get().strip() or None


def ask_remove_subject(parent, title=None, message=None, icon_path=None):
    """Creates the remove subject dialog and returns the input value."""
    dialog = RemoveSubjectDialog(parent, title, message, icon_path)
    return dialog.result


def ask_add_subject(parent, title=None, message=None, icon_path=None):
    dialog = AddSubjectDialog(parent, title, message, icon_path)
    return dialog.result["subject_code"], dialog.result["subject_name"], dialog.result["sync_source"]


def ask_add_total_mark(parent, title=None, message=None, icon_path=None):
    dialog = AddTotalMarkDialog(parent, title, message, icon_path)
    return dialog.result
