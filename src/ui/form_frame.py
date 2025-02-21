import tkinter as tk
from tkinter import ttk


def create_form_frame(main_frame: ttk.Frame, sheet_var: tk.StringVar, year_var: tk.StringVar,
                      semesters: dict, year_list: list, update_year, update_semester) -> None:
    form_frame = ttk.Frame(main_frame)
    form_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    sheet_label = ttk.Label(form_frame, text="Select Semester:")
    sheet_label.grid(row=0, column=0, padx=2, pady=2, sticky=tk.W)

    semester_menu = ttk.OptionMenu(form_frame, sheet_var,
                                   list(semesters.keys())[0],
                                   *list(semesters.keys()),
                                   command=update_semester)
    semester_menu.grid(row=0, column=1, padx=2, pady=2, sticky=tk.W)

    year_label = ttk.Label(form_frame, text="Select Year:")
    year_label.grid(row=0, column=2, padx=2, pady=2, sticky=tk.W)

    year_menu = ttk.OptionMenu(form_frame, year_var,
                               year_var.get(),
                               *year_list,
                               command=update_year)
    year_menu.grid(row=0, column=3, padx=2, pady=2, sticky=tk.W)
