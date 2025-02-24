import customtkinter as ctk


class AddSubjectDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Subject")
        self.transient(parent)
        self.grab_set()  # Make the dialog modal
        self.geometry("500x150")
        self.resizable(False, False)

        self.subject_code = None
        self.subject_name = None

        # Use customtkinter widgets so the theme matches the root
        code_label = ctk.CTkLabel(self, text="Subject Code:")
        code_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.entry_code = ctk.CTkEntry(self)
        self.entry_code.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="ew")

        name_label = ctk.CTkLabel(self, text="Subject Name:")
        name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_name = ctk.CTkEntry(self)
        self.entry_name.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ok_button = ctk.CTkButton(button_frame, text="OK", command=self.on_ok)
        ok_button.grid(row=0, column=0, padx=5)
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.on_cancel)
        cancel_button.grid(row=0, column=1, padx=5)

        # Allow the entry widget column to expand
        self.columnconfigure(1, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_ok(self):
        self.subject_code = self.entry_code.get().strip() or None
        self.subject_name = self.entry_name.get().strip() or None
        self.destroy()

    def on_cancel(self):
        self.subject_code = None
        self.subject_name = None
        self.destroy()


def ask_add_subject(parent):
    dialog = AddSubjectDialog(parent)
    parent.wait_window(dialog)
    return dialog.subject_code, dialog.subject_name
