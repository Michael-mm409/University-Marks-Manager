#### style_config.py ####
import tkinter as tk
from tkinter import ttk

def configure_styles(root: tk.Tk):
    style = ttk.Style(root)
    style.theme_use("clam")  # Start with 'clam' theme
    
    # Customize the styles for dark mode
    dark_bg = "#2e2e2e"
    dark_fg = "#ffffff"
    accent_color = "#0078D7"
    hover_color = "#3399FF"

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