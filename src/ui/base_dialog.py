from tkinter import simpledialog

import customtkinter as ctk


class BaseDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, icon_path=None, geometry="250x150", resizable=(True, False)):
        self.icon_path = icon_path
        self.result = None
        self.geometry_size = geometry
        self.resizable_flags = resizable
        super().__init__(parent, title=title)

    def body(self, master):
        # Set the background color for the dialog
        master.configure(background="#0D1B2A")

        # Set the icon for the dialog
        if self.icon_path:
            self.iconbitmap(self.icon_path)

        # Set the window size and aspect ratio
        self.geometry(self.geometry_size)
        self.resizable(*self.resizable_flags)

        # Create a button frame
        self.button_frame = ctk.CTkFrame(master, fg_color="#0D1B2A", width=1500)
        self.button_frame.pack_propagate(False)
        self.button_frame.pack(fill="both", expand=True)

    def buttonbox(self):
        # Add OK and Cancel buttons to the button_frame
        ctk.CTkButton(self.button_frame, text="OK", command=self.ok, fg_color="#1D3557", text_color="white").pack(
            side="left", fill="x", expand=True, padx=5
        )
        ctk.CTkButton(
            self.button_frame, text="Cancel", command=self.cancel, fg_color="#1D3557", text_color="white"
        ).pack(side="right", fill="x", expand=True, padx=5)
