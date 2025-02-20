#### treeview_setup.py ####
import tkinter as tk
from tkinter import ttk

def create_treeview(main_frame: ttk.Frame) -> ttk.Treeview:
    treeview = ttk.Treeview(main_frame,
                            columns=("Subject Code", "Subject Name", "Subject Assessment", 
                                     "Unweighted Mark","Weighted Mark", 
                                     "Mark Weight", "Total Mark"),
                            show="headings", height=15)
    treeview.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    headings = {
        "Subject Code": "Subject Code",
        "Subject Name": "Subject Name",
        "Subject Assessment": "Subject Assessment",
        "Unweighted Mark": "Mark (Out of Full Score)",
        "Weighted Mark": "Weighted Contribution (%)",
        "Mark Weight": "Assessment Weight (e.g., 30%)",
        "Total Mark": "Total Mark"
    }

    for col, description in headings.items():
        treeview.heading(col, text=description)
        treeview.column(col, anchor=tk.CENTER)

    return treeview