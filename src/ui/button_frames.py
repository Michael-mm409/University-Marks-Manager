#### button_frames.py ####
import tkinter as tk
from tkinter import ttk

def create_button_frames(main_frame: ttk.Frame, application_self) -> None:
    subject_button_frame = ttk.Frame(main_frame)
    subject_button_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

    add_subject_btn = ttk.Button(subject_button_frame,
                                 text="Add Subject",
                                 compound=tk.LEFT,
                                 command=application_self.add_subject)
    add_subject_btn.grid(row=0, column=0, padx=2, pady=2)

    remove_subject_btn = ttk.Button(subject_button_frame,
                                    text="Remove Subject",
                                    compound=tk.LEFT,
                                    command=application_self.remove_subject)
    remove_subject_btn.grid(row=0, column=1, padx=2, pady=2)

    add_semester_btn = ttk.Button(subject_button_frame,
                                  text="Add Semester",
                                  compound=tk.LEFT,
                                  command=application_self.add_semester)
    add_semester_btn.grid(row=0, column=2, padx=2, pady=2)

    remove_semester_btn = ttk.Button(subject_button_frame,
                                     text="Remove Semester",
                                     compound=tk.LEFT,
                                     command=application_self.remove_semester)
    remove_semester_btn.grid(row=0, column=3, padx=2, pady=2)

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

    add_entry_btn = ttk.Button(button_frame,
                               text="Add Entry",
                               compound=tk.LEFT,
                               command=application_self.add_entry)
    add_entry_btn.grid(row=0, column=0, padx=2, pady=2)

    del_btn = ttk.Button(button_frame,
                         text="Delete Entry",
                         compound=tk.LEFT,
                         command=application_self.delete_entry)
    del_btn.grid(row=0, column=1, padx=2, pady=2)

    calc_btn = ttk.Button(button_frame,
                          text="Calculate Exam Mark",
                          compound=tk.LEFT,
                          command=application_self.calculate_exam_mark)
    calc_btn.grid(row=0, column=2, padx=2, pady=2)