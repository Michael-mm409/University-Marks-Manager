import customtkinter as ctk
from tkinter import ttk


def create_entry_frame(main_frame: ttk.Frame,
                       application_self) -> None:
    entry_frame = ctk.CTkFrame(main_frame)
    entry_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    fields = [
        ("Subject Code", "subject_code_entry"),
        ("Subject Assessment", "subject_assessment_entry"),
        ("Weighted Mark", "weighted_mark_entry"),
        ("Mark Weight (%)", "mark_weight_entry"),
        ("Total Mark", "total_mark_entry"),
    ]

    for i, (field, attr) in enumerate(fields):
        label = ctk.CTkLabel(entry_frame, text=f"{field}:")
        label.grid(row=i // 2, column=(i % 2) * 2, padx=2, pady=2, sticky="w")
        entry = ctk.CTkEntry(entry_frame, width=50)
        entry.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=2, pady=2, sticky="ew")
        setattr(application_self, attr, entry)

    # Add a checkbox for sync source with the existing style
    application_self.sync_source_var = ctk.BooleanVar()
    sync_source_checkbox = ctk.CTkCheckBox(entry_frame,
                                           text="Sync Subject Across All Semesters",
                                           variable=application_self.sync_source_var)
    sync_source_checkbox.grid(row=3, column=0, columnspan=2, padx=2, pady=2, sticky="w")

    # Configure column weight
    entry_frame.grid_columnconfigure(1, weight=1)

    # Configure entry field columns (columns 1 and 3) to share the available space
    entry_frame.grid_columnconfigure(1, weight=1)
    entry_frame.grid_columnconfigure(3, weight=1)
