import os
from tkinter import simpledialog

import customtkinter as ctk


class BaseDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, icon_path=None, geometry="250x150", resizable=(True, False)):
        # Resolve the absolute path of the icon
        if icon_path and os.path.isfile(icon_path):
            self.icon_path = os.path.abspath(icon_path)
        else:
            self.icon_path = None
            print(f"Warning: Invalid or missing icon path '{icon_path}'.")

        # Validate the geometry string
        if isinstance(geometry, str) and "x" in geometry:
            self.geometry_size = geometry
        else:
            print(f"Warning: Invalid geometry '{geometry}'. Using default '250x150'.")
            self.geometry_size = "250x150"

        self.resizable_flags = resizable
        self.result = None
        super().__init__(parent, title=title)

    def body(self, master):
        # Set the background color for the dialog
        master.configure(background="#0D1B2A")

        # Set the icon for the dialog
        if self.icon_path:
            try:
                self.iconbitmap(self.icon_path)
            except Exception as e:
                print(f"Warning: Failed to set icon '{self.icon_path}'. Error: {e}")

        # Set the window size and aspect ratio
        self.geometry(self.geometry_size)
        self.resizable(*self.resizable_flags)

        # Create a button frame
        self.button_frame = ctk.CTkFrame(master, fg_color="#0D1B2A", width=1500)
        self.button_frame.pack_propagate(False)
        self.button_frame.pack(fill="both", expand=True)

        return self.button_frame  # Ensure the button frame is returned for subclasses to use

    def buttonbox(self):
        """Add OK and Cancel buttons to the dialog."""
        if not hasattr(self, "button_frame"):
            raise AttributeError("button_frame is not defined. Ensure the body method is called first.")

        ctk.CTkButton(self.button_frame, text="OK", command=self.ok, fg_color="#1D3557", text_color="white").pack(
            side="left", fill="x", expand=True, padx=5
        )
        ctk.CTkButton(
            self.button_frame, text="Cancel", command=self.cancel, fg_color="#1D3557", text_color="white"
        ).pack(side="right", fill="x", expand=True, padx=5)
