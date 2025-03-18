import customtkinter as ctk

from .base_dialog import BaseDialog


class AddSemesterDialog(BaseDialog):
    def body(self, master):
        super().body(master)  # Call the base class body method

        # Add custom UI elements for AddSemesterDialog
        ctk.CTkLabel(
            self.button_frame, text="Enter the name of the new semester:", fg_color="#0D1B2A", text_color="white"
        ).pack(side="top", anchor="w", padx=10, pady=5)

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


def ask_add_semester(parent, title=None, message=None, icon_path="./assets/app_icon.ico"):
    dialog = AddSemesterDialog(parent, title, message, icon_path)
    return dialog.result


def ask_confirm(parent, title=None, message=None, icon_path=None):
    dialog = __ConfirmDialog(parent, title=title, message=message, icon_path=icon_path)
    return dialog.result
