from tkinter import simpledialog

import customtkinter as ctk


class __AddSubjectDialog(simpledialog.Dialog):
    def __init__(self, parent, icon_path=None):
        self.icon_path = icon_path
        self.subject_code = None
        self.subject_name = None
        super().__init__(parent, title="Add Subject")

    def body(self, master):
        # Set the icon for the dialog
        if self.icon_path:
            self.iconbitmap(self.icon_path)

        # UI Elements
        ctk.CTkLabel(master, text="Subject Code:").grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.entry_code = ctk.CTkEntry(master)
        self.entry_code.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="ew")

        ctk.CTkLabel(master, text="Subject Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_name = ctk.CTkEntry(master)
        self.entry_name.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        return self.entry_code  # initial focus

    def apply(self):
        self.subject_code = self.entry_code.get().strip() or None
        self.subject_name = self.entry_name.get().strip() or None


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


def ask_add_subject(parent, icon_path=None):
    dialog = __AddSubjectDialog(parent, icon_path)
    return dialog.subject_code, dialog.subject_name


def ask_add_total_mark(parent, icon_path=None):
    dialog = __AddTotalMarkDialog(parent, icon_path)
    return dialog.total_mark
