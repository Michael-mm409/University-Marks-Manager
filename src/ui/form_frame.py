from customtkinter import CTkOptionMenu, CTkLabel, CTkFrame, StringVar
import customtkinter as ctk


def create_form_frame(
    self,
    main_frame: CTkFrame,
    sheet_var: StringVar,
    year_var: StringVar,
    semesters: dict,
    year_list: list,
    update_year,
    update_semester,
) -> None:
    form_frame = CTkFrame(main_frame, fg_color="#0D1B2A")
    form_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    sheet_label = CTkLabel(form_frame, text="Select Semester:")
    sheet_label.grid(row=0, column=0, padx=2, pady=2, sticky=ctk.W)

    self.semester_menu = CTkOptionMenu(
        form_frame, variable=sheet_var, values=sorted(semesters.keys()), command=update_semester)

    self.semester_menu.grid(row=0, column=1, padx=2, pady=2, sticky=ctk.W)

    year_label = CTkLabel(form_frame, text="Select Year:")
    year_label.grid(row=0, column=2, padx=2, pady=2, sticky=ctk.W)

    year_menu = CTkOptionMenu(form_frame, variable=year_var, values=year_list, command=update_year)
    year_menu.grid(row=0, column=3, padx=2, pady=2, sticky=ctk.W)
