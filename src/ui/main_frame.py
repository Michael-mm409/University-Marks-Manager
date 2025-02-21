import tkinter as tk
from tkinter import ttk


def create_main_frame(root: tk.Tk) -> ttk.Frame:
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky="nsew")
    return main_frame
