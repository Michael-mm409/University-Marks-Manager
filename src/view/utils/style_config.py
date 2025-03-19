import customtkinter as ctk
from tkinter import ttk
from os import path, getcwd


def configure_styles(root: ctk.CTk):
    # Set the appearance mode and default theme using customtkinter.
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    # Optionally remove or update calls for the ttk theme if they conflict.
    style = ttk.Style(root)
    theme_path = path.join(getcwd(), 'Azure-ttk-theme-main', 'azure.tcl')
    root.tk.call("source", theme_path)
    root.tk.call("set_theme", "dark")

    # Define color variables for the dark blue palette.
    dark_bg = "#0D1B2A"       # Dark blue background
    dark_fg = "#ffffff"       # White foreground
    accent_color = "#1B263B"  # Slightly lighter blue for accents
    hover_color = "#415A77"   # Blue tone for hover states

    # Set the default font for the entire application
    default_font = ("Helvetica", 14)
    root.option_add("*Font", default_font)

    style.configure("TFrame", background=dark_bg, font=default_font)
    style.configure("TLabel", background=dark_bg, foreground=dark_fg, font=default_font)
    style.configure("TButton",
                    background=accent_color,
                    foreground=dark_fg,
                    font=default_font,
                    relief="flat")
    style.map("TButton",
              background=[("active", hover_color), ("focus", accent_color)],
              foreground=[("active", dark_fg), ("focus", dark_fg)],
              highlightbackground=[("active", hover_color), ("focus", accent_color)],
              highlightcolor=[("active", hover_color), ("focus", accent_color)],
              )

    style.configure("TCheckbutton",
                    background=dark_bg,
                    foreground=dark_fg,
                    font=default_font,
                    selectcolor=dark_bg,
                    relief="flat")
    style.map("TCheckbutton",
              background=[("active", dark_bg), ("focus", dark_bg)],
              foreground=[("active", dark_fg), ("focus", dark_fg)],
              highlightbackground=[("active", dark_bg), ("focus", dark_bg)],
              highlightcolor=[("active", dark_bg), ("focus", dark_bg)])

    style.configure("Treeview", background=dark_bg, foreground=dark_fg, fieldbackground=dark_bg, font=default_font)
    style.configure("Treeview.Heading", background=accent_color, foreground=dark_fg, font=(default_font[0], 16))

    style.configure("Card.TFrame", background=dark_bg, highlightbackground=dark_bg,
                    highlightcolor=dark_bg, font=default_font)
    style.map("Card.TFrame",
              background=[("active", hover_color), ("focus", accent_color)],
              highlightbackground=[("active", hover_color), ("focus", accent_color)],
              highlightcolor=[("active", hover_color), ("focus", accent_color)])
