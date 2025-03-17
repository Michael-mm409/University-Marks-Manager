from tkinter import simpledialog

import customtkinter as ctk


class __AddSemesterDialog(simpledialog.Dialog):
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
        ctk.CTkLabel(
            self.button_frame, text="Enter the name of the new semester:", fg_color="#0D1B2A", text_color="white"
        ).pack(
            side="top",
            anchor="w",
            padx=10,
            pady=5,
        )
        self.semester_name = ctk.CTkEntry(self.button_frame, fg_color="#0D1B2A", text_color="white")
        self.semester_name.pack(fill="x", padx=10)

        return self.semester_name  # Set initial focus

    def buttonbox(self):
        # Add OK and Cancel buttons to the button_frame
        ctk.CTkButton(self.button_frame, text="OK", command=self.ok, fg_color="#1D3557", text_color="white").pack(
            side="left", fill="x", expand=True, padx=5
        )
        ctk.CTkButton(
            self.button_frame, text="Cancel", command=self.cancel, fg_color="#1D3557", text_color="white"
        ).pack(side="right", fill="x", expand=True, padx=5)

    def apply(self):
        self.semester_name = self.semester_name.get()


class __ConfirmDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, message=None, icon_path=None):
        self.icon_path = icon_path
        self.message = message
        self.result = False
        super().__init__(parent, title=title)

    def body(self, master):
        # Set the background color for the dialog
        master.configure(background="#0D1B2A")

        # Set the icon for the dialog
        if self.icon_path:
            self.iconbitmap(self.icon_path)

        # Set the window size to accommodate the frame width
        self.geometry("320x120")  # Increased height to 150
        self.resizable(False, False)

        # Create a frame for the message and buttons
        self.message_frame = ctk.CTkFrame(master, fg_color="#0D1B2A")
        self.message_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Display the message
        ctk.CTkLabel(self.message_frame, text=self.message, fg_color="#0D1B2A", text_color="white").pack(
            side="top", anchor="w", padx=10, pady=5
        )

        return self.message_frame

    def buttonbox(self):
        # Add Yes and No buttons to the button_frame
        button_frame = ctk.CTkFrame(self.message_frame, fg_color="#0D1B2A")
        button_frame.pack(side="bottom", fill="x")

        ctk.CTkButton(button_frame, text="Yes", command=self.yes, fg_color="#1D3557", text_color="white").pack(
            side="left", fill="x", expand=True, padx=5
        )

        ctk.CTkButton(button_frame, text="No", command=self.no, fg_color="#1D3557", text_color="white").pack(
            side="right", fill="x", expand=True, padx=5
        )

    def yes(self):
        self.result = True
        self.ok()

    def no(self):
        self.result = False
        self.cancel()


def ask_add_semester(parent, icon_path=None):
    dialog = __AddSemesterDialog(parent, icon_path)
    return dialog.semester_name


def ask_confirm(parent, title=None, message=None, icon_path=None):
    dialog = __ConfirmDialog(parent, title=title, message=message, icon_path=icon_path)
    return dialog.result
