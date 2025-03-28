from tkinter import messagebox, simpledialog
from typing import Any


def validate_float(value: Any, error_message: str, default_value: float = 0) -> float:
    if value is None or value == "":
        messagebox.showwarning("Warning", f"No value entered. Defaulting to {default_value}.")
        return default_value
    try:
        return float(value)  # Return the valid float
    except ValueError:
        messagebox.showerror("Error", error_message)  # Show error message
        # Re-prompt the user for input
        return validate_float(
            simpledialog.askstring("Input", error_message + " Please enter a valid number."),
            error_message,
            default_value,
        )
