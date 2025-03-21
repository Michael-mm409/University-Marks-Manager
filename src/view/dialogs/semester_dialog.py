import customtkinter as ctk
from tkinter import simpledialog

from .base_dialog import BaseDialog


class AddSemesterDialog(BaseDialog):
    def __init__(self, parent, title=None, message=None, icon_path=None):
        self.message = message
        super().__init__(parent, icon_path=icon_path, title=title)

    def body(self, master):
        super().body(master)  # Call the base class body method

        # Add custom UI elements for AddSemesterDialog
        ctk.CTkLabel(self.button_frame, text=self.message, fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w", padx=10
        )

        self.entry_semester_name = ctk.CTkEntry(self.button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_semester_name.pack(fill="x", padx=10)

        return self.entry_semester_name  # Set initial focus

    def apply(self):
        self.result = self.entry_semester_name.get().strip() or None


class __ConfirmDialog(BaseDialog):
    def __init__(self, parent, title=None, message=None, icon_path=None):
        self.message = message
        super().__init__(parent, icon_path=icon_path, title=title)

    def body(self, master):
        super().body(master)  # Call the base class body method

        # Display the message
        ctk.CTkLabel(self.button_frame, text=self.message, fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w"
        )

        return self.button_frame

    def buttonbox(self):
        # Add Yes and No buttons to the button_frame
        ctk.CTkButton(self.button_frame, text="Yes", command=self.yes, fg_color="#1D3557", text_color="white").pack(
            side="left", fill="x", expand=True, padx=5
        )
        ctk.CTkButton(self.button_frame, text="No", command=self.no, fg_color="#1D3557", text_color="white").pack(
            side="right", fill="x", expand=True, padx=5
        )

    def yes(self):
        self.result = True
        self.ok()

    def no(self):
        self.result = False
        self.cancel()


class SemesterSelectionDialog(simpledialog.Dialog):
    def __init__(self, parent, available_semesters, icon_path=None):
        self.available_semesters = available_semesters
        self.selected_semesters = []
        self.custom_semesters = []  # To store custom semesters
        self.icon_path = icon_path
        super().__init__(parent, title="Select Semesters")

    def body(self, master):
        if self.icon_path:
            self.iconbitmap(self.icon_path)

        # Label for predefined semesters
        ctk.CTkLabel(master, text="Select the semesters to include:").grid(row=0, column=0, columnspan=2,
                                                                           padx=10, pady=10)

        # Checkboxes for predefined semesters
        self.check_vars = {}
        for i, semester in enumerate(self.available_semesters):
            var = ctk.BooleanVar(value=False)
            self.check_vars[semester] = var
            ctk.CTkCheckBox(master, text=semester, variable=var).grid(row=i + 1, column=0, sticky="w", padx=10)

        # Label for custom semesters
        custom_semesters_label = ctk.CTkLabel(master, text="Other Semesters (comma-separated):")
        custom_semesters_label.grid(row=len(self.available_semesters) + 1, column=0, columnspan=2,
                                    padx=10, pady=(10, 5))

        # Entry for custom semesters
        self.custom_semesters_entry = ctk.CTkEntry(master, width=300)
        self.custom_semesters_entry.grid(row=len(self.available_semesters) + 2, column=0, columnspan=2, padx=10, pady=5)

        return None

    def apply(self):
        # Get selected predefined semesters
        self.selected_semesters = [semester for semester, var in self.check_vars.items() if var.get()]

        # Get custom semesters from the text box
        custom_semesters_text = self.custom_semesters_entry.get().strip()
        if custom_semesters_text:
            self.custom_semesters = [semester.strip() for semester in custom_semesters_text.split(",")
                                     if semester.strip()]

        # Combine predefined and custom semesters
        self.selected_semesters.extend(self.custom_semesters)


def ask_add_semester(parent, title=None, message=None, icon_path="./assets/app_icon.ico"):
    dialog = AddSemesterDialog(parent=parent, title=title, message=message, icon_path=icon_path)
    return dialog.result


def ask_confirm(parent, title=None, message=None, icon_path=None):
    dialog = __ConfirmDialog(parent, title=title, message=message, icon_path=icon_path)
    return dialog.result


def ask_semesters(parent, icon_path=None):
    available_semesters = ["Autumn", "Spring", "Annual", "Summer"]
    dialog = SemesterSelectionDialog(parent, available_semesters, icon_path)
    return dialog.selected_semesters
