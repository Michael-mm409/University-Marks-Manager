import tkinter as tk
from tkinter import ttk
from customtkinter import CTkFrame


def create_main_frame(root: tk.Tk) -> ttk.Frame:
    main_frame = CTkFrame(root, fg_color="#0D1B2A")
    main_frame.grid(row=0, column=0, sticky="nsew")
    return main_frame
