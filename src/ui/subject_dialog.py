from tkinter import simpledialog

import customtkinter as ctk


class __AddSubjectDialog(simpledialog.Dialog):
    def __init__(self, parent, icon_path=None):
        self.icon_path = icon_path
        self.subject_code = None
        self.subject_name = None
        self.sync_source = None
        super().__init__(parent, title="Add Subject")

    def body(self, master):
        # Set the background color for the dialog
        master.configure(background="#0D1B2A")

        # Set the icon for the dialog
        if self.icon_path:
            self.iconbitmap(self.icon_path)

        # Set the window size to accommodate the frame width
        self.geometry("250x200")  # Adjusted the height to accommodate the checkbox
        self.resizable(True, True)  # Make the dialog resizable

        # Create a larger button frame with adjustable width
        self.button_frame = ctk.CTkFrame(master, fg_color="#0D1B2A", width=1500)
        self.button_frame.pack_propagate(False)
        self.button_frame.pack(fill="both", expand=True)

        # UI Elements
        ctk.CTkLabel(self.button_frame, text="Subject Code:", fg_color="#0D1B2A", text_color="white").pack(
            side="top",
            anchor="w",
            padx=10,
            pady=5,
        )
        self.entry_code = ctk.CTkEntry(self.button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_code.pack(fill="x", padx=10)

        ctk.CTkLabel(self.button_frame, text="Subject Name:", fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w", padx=10
        )
        self.entry_name = ctk.CTkEntry(self.button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_name.pack(fill="x", padx=10)

        # Add sync source checkbox
        self.sync_source_var = ctk.BooleanVar()
        ctk.CTkCheckBox(
            self.button_frame, text="Sync Subject Across All Semesters", variable=self.sync_source_var
        ).pack(side="top", anchor="w", padx=10, pady=5)

        return self.entry_code  # Set initial focus

    def buttonbox(self):
        # Add OK and Cancel buttons to the button_frame
        ctk.CTkButton(self.button_frame, text="OK", command=self.ok, fg_color="#1D3557", text_color="white").pack(
            side="left", fill="x", expand=True, padx=5
        )
        ctk.CTkButton(
            self.button_frame, text="Cancel", command=self.cancel, fg_color="#1D3557", text_color="white"
        ).pack(side="right", fill="x", expand=True, padx=5)

    def apply(self):
        self.subject_code = self.entry_code.get().strip() or None
        self.subject_name = self.entry_name.get().strip() or None
        self.sync_source = self.sync_source_var.get()


class __AddTotalMarkDialog(simpledialog.Dialog):
    def __init__(self, parent, icon_path=None):
        self.icon_path = icon_path
        self.total_mark = None
        super().__init__(parent, title="Add Total Mark")

    def body(self, master):
        if self.icon_path:
            self.iconbitmap(self.icon_path)

        ctk.CTkLabel(master, text="Enter Total Mark:").grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.entry_total_mark = ctk.CTkEntry(master)
        self.entry_total_mark.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="ew")
        return self.entry_total_mark

    def apply(self):
        self.total_mark = self.entry_total_mark.get().strip() or None


class RemoveSubjectDialog(simpledialog.Dialog):
    def __init__(self, parent, icon_path=None):
        self.icon_path = icon_path
        self.subject_code = None
        super().__init__(parent, title="Remove Subject")

    def body(self, master):
        # Set the background color for the dialog
        master.configure(background="#0D1B2A")

        # Set the icon for the dialog
        if self.icon_path:
            self.iconbitmap(self.icon_path)

        # Set the window size to accommodate the frame width
        self.geometry("250x150")  # Adjusted the height to accommodate the input field
        self.resizable(True, True)  # Make the dialog resizable

        # Create a larger button frame with adjustable width
        self.button_frame = ctk.CTkFrame(master, fg_color="#0D1B2A", width=1500)
        self.button_frame.pack_propagate(False)
        self.button_frame.pack(fill="both", expand=True)

        # UI Elements
        ctk.CTkLabel(self.button_frame, text="Subject Code:", fg_color="#0D1B2A", text_color="white").pack(
            side="top",
            anchor="w",
            padx=10,
            pady=5,
        )
        self.entry_code = ctk.CTkEntry(self.button_frame, fg_color="#0D1B2A", text_color="white")
        self.entry_code.pack(fill="x", padx=10)

        return self.entry_code  # Set initial focus

    def buttonbox(self):
        # Add OK and Cancel buttons to the button_frame
        ctk.CTkButton(self.button_frame, text="OK", command=self.ok, fg_color="#1D3557", text_color="white").pack(
            side="left", fill="x", expand=True, padx=5, pady=10
        )
        ctk.CTkButton(
            self.button_frame, text="Cancel", command=self.cancel, fg_color="#1D3557", text_color="white"
        ).pack(side="right", fill="x", expand=True, padx=5, pady=10)

    def apply(self):
        self.subject_code = self.entry_code.get().strip() or None


def ask_remove_subject(parent, icon_path=None):
    """Creates the remove subject dialog and returns the input value."""
    dialog = RemoveSubjectDialog(parent, icon_path)
    parent.wait_window(dialog)  # Wait for the dialog window to close
    return dialog.subject_code


def ask_add_subject(parent, icon_path=None):
    dialog = __AddSubjectDialog(parent, icon_path)
    return dialog.subject_code, dialog.subject_name, dialog.sync_source


def ask_add_total_mark(parent, icon_path=None):
    dialog = __AddTotalMarkDialog(parent, icon_path)
    return dialog.total_mark
