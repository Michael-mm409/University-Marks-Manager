import tkinter as tk
from tkinter import ttk


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
    subject_button_frame = ttk.Frame(main_frame)
    subject_button_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

    add_subject_btn = ttk.Button(subject_button_frame, text="Add Subject", compound=tk.LEFT, command=add_subject_func)
    add_subject_btn.grid(row=0, column=0, padx=2, pady=2)

    remove_subject_btn = ttk.Button(
        subject_button_frame, text="Remove Subject", compound=tk.LEFT, command=remove_subject_func
    )
    remove_subject_btn.grid(row=0, column=1, padx=2, pady=2)

    add_semester_btn = ttk.Button(
        subject_button_frame, text="Add Semester", compound=tk.LEFT, command=add_semester_func
    )
    add_semester_btn.grid(row=0, column=2, padx=2, pady=2)

    remove_semester_btn = ttk.Button(
        subject_button_frame, text="Remove Semester", compound=tk.LEFT, command=remove_semester_func
    )
    remove_semester_btn.grid(row=0, column=3, padx=2, pady=2)

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

    add_entry_btn = ttk.Button(button_frame, text="Add Entry", compound=tk.LEFT, command=add_entry_func)
    add_entry_btn.grid(row=0, column=0, padx=2, pady=2)

    del_btn = ttk.Button(button_frame, text="Delete Entry", compound=tk.LEFT, command=delete_entry_func)
    del_btn.grid(row=0, column=1, padx=2, pady=2)

    calc_btn = ttk.Button(button_frame, text="Calculate Exam Mark", compound=tk.LEFT, command=calculate_exam_mark_func)
    calc_btn.grid(row=0, column=2, padx=2, pady=2)

    add_total_mark = ttk.Button(button_frame, text="Add Total Mark", compound=tk.LEFT, command=add_total_mark_func)
    add_total_mark.grid(row=0, column=3, padx=2, pady=2)
