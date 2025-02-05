import tkinter as tk
from application import Application
from data_persistence import DataPersistence
from datetime import datetime

if __name__ == "__main__":
    root = tk.Tk()

    # Enable window resizing (set both width and height to True)
    root.resizable(width=True, height=True)

    root.title("University Marks Manager")
    data_persistence = DataPersistence(str(datetime.now().year), use_tinydb=True)  # Year is set as 2024 for demonstration
    app = Application(root, data_persistence)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()

