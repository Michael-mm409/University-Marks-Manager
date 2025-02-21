import customtkinter as tk


class ToolTipManager:
    """
    A class to represent a tooltip for displaying 
    additional information when hovering over a widget.

    Args:
        widget (tk.Widget): The widget to which the tooltip is attached.
        text (str): The text to be displayed in the tooltip.
        tip_window (tk.Toplevel): The tooltip window to display the text.
    """
    def __init__(self, widget: tk.Widget, text: str):
        """
        Constructs all the necessary attributes for the tooltip window.

        Args:
            widget (tk.Widget): The widget to which the tooltip is attached.
            text (str): The text to be displayed in the tooltip.
        """
        self.widget = widget
        self.text = text
        self.tip_window = None

    def show_tip(self, event: tk.Event):
        """
        Displays the tooltip window with the specified text.

        Args:
            event (tk.Event): The event that triggered the tooltip display.
        """
        if self.tip_window or not self.text:
            return
        x = event.x_root + 10
        y = event.y_root + 10
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="yellow", relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hide_tip(self, _event):
        """
        Hides the tooltip window when the mouse leaves the widget.

        Args:
            _event (tk.Event): The event that triggered the tooltip hide action.
        """
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
