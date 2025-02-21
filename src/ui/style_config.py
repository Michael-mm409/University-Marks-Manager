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

    style.configure("TFrame", background=dark_bg)
    style.configure("TLabel", background=dark_bg, foreground=dark_fg, font=("Helvetica", 12))
    style.configure("TButton",
                    background=accent_color,
                    foreground=dark_fg,
                    font=("Helvetica", 12),
                    relief="flat")
    style.map("TButton",
              background=[("active", hover_color), ("focus", accent_color)],
              foreground=[("active", dark_fg), ("focus", dark_fg)],
              highlightbackground=[("active", hover_color), ("focus", accent_color)],
              highlightcolor=[("active", hover_color), ("focus", accent_color)])

    style.configure("TCheckbutton",
                    background=dark_bg,
                    foreground=dark_fg,
                    font=("Helvetica", 12),
                    selectcolor=dark_bg,
                    relief="flat")
    style.map("TCheckbutton",
              background=[("active", dark_bg), ("focus", dark_bg)],
              foreground=[("active", dark_fg), ("focus", dark_fg)],
              highlightbackground=[("active", dark_bg), ("focus", dark_bg)],
              highlightcolor=[("active", dark_bg), ("focus", dark_bg)])

    style.configure("Treeview", background=dark_bg, foreground=dark_fg, fieldbackground=dark_bg)
    style.configure("Treeview.Heading", background=accent_color, foreground=dark_fg)

    style.configure("Card.TFrame", background=dark_bg, highlightbackground=dark_bg, highlightcolor=dark_bg)
    style.map("Card.TFrame",
              background=[("active", hover_color), ("focus", accent_color)],
              highlightbackground=[("active", hover_color), ("focus", accent_color)],
              highlightcolor=[("active", hover_color), ("focus", accent_color)])

    # Create a topbar frame
    topbar_frame = ttk.Frame(root, style="Card.TFrame")
    topbar_frame.grid(row=0, column=0, sticky="ew")
