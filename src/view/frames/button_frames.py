import tkinter as tk
from tkinter import ttk
from customtkinter import CTkFrame, CTkButton


def create_button_frames(
    main_frame: ttk.Frame,
    add_subject_func,
    remove_subject_func,
    add_semester_func,
    remove_semester_func,
    add_entry_func,
    delete_entry_func,
    calculate_exam_mark_func,
    add_total_mark_func,
) -> None:
    dark_bg = "#0D1B2A"       # Dark blue background
    button_frame = CTkFrame(main_frame, fg_color=dark_bg)
    button_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

    add_subject_btn = CTkButton(button_frame, text="Add Subject", compound=tk.LEFT, command=add_subject_func)
    add_subject_btn.grid(row=0, column=0, padx=2, pady=2)

    remove_subject_btn = CTkButton(
        button_frame, text="Remove Subject", compound=tk.LEFT, command=remove_subject_func
    )
    remove_subject_btn.grid(row=0, column=1, padx=2, pady=2)

    add_semester_btn = CTkButton(
        button_frame, text="Add Semester", compound=tk.LEFT, command=add_semester_func
    )
    add_semester_btn.grid(row=0, column=2, padx=2, pady=2)

    remove_semester_btn = CTkButton(
        button_frame, text="Remove Semester", compound=tk.LEFT, command=remove_semester_func
    )
    remove_semester_btn.grid(row=0, column=3, padx=2, pady=2)

    add_entry_btn = CTkButton(button_frame, text="Add Entry", compound=tk.LEFT, command=add_entry_func)
    add_entry_btn.grid(row=1, column=0, padx=2, pady=2)

    del_btn = CTkButton(button_frame, text="Delete Entry", compound=tk.LEFT, command=delete_entry_func)
    del_btn.grid(row=1, column=1, padx=2, pady=2)

    calc_btn = CTkButton(button_frame, text="Calculate Exam Mark", compound=tk.LEFT, command=calculate_exam_mark_func)
    calc_btn.grid(row=1, column=2, padx=2, pady=2)

    add_total_mark = CTkButton(button_frame, text="Add Total Mark", compound=tk.LEFT, command=add_total_mark_func)
    add_total_mark.grid(row=1, column=3, padx=2, pady=2)
