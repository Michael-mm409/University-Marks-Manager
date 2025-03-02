import colorsys
import tkinter as tk
from typing import Tuple


def brighten_color(hex_color: str, factor: float = 0.3) -> str:
    """
    Brighten a hex color by a given factor.

    Args:
        hex_color (str): The hex color to brighten.
        factor (float): The factor by which to brighten the color.

    Returns:
        str: The brightened hex color.
    """
    # Remove the '#' character from the beginning of the hex color string
    hex_color = hex_color.lstrip("#")

    # Covnert the hex color to RGB tuple
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    # Convert the RGB color to HLS color space (Hue, Lightness, Saturation)
    hls = colorsys.rgb_to_hls(*[x / 255.0 for x in rgb])

    # Increase the lightness component of the HLS color by the specified factor
    rgb_bright = colorsys.hls_to_rgb(hls[0], min(1, hls[1] + factor * (1 - hls[1])), hls[2])

    # Convert the brighted HLS color back to RGB color space
    rgb_bright = tuple(int(x * 255) for x in rgb_bright)

    # Convert the RGB color back to a hex color string and return it
    return "#{:02x}{:02x}{:02x}".format(*rgb_bright)


class ToolTipManager:
    """
    A class to represent a tooltip for displaying
    additional information when hovering over a widget.

    Args:
        widget (tk.Widget): The widget to which the tooltip is attached.
        text (str): The text to be displayed in the tooltip.
        tip_window (tk.Toplevel): The tooltip window to display the text.
    """

    def __init__(
        self,
        widget: tk.Widget,
        text: str,
        bg_color: str = "#0D1B2A",
        fg_color: str = "white",
        font: Tuple[str, int] = ("Arial", 10),
    ):
        """
        Constructs all the necessary attributes for the tooltip window.

        Args:
            widget (tk.Widget): The widget to which the tooltip is attached.
            text (str): The text to be displayed in the tooltip.
        """
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.bg_color = brighten_color(bg_color)  # Brighten the background color
        self.fg_color = fg_color
        self.font = font

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
        label = tk.Label(
            tw,
            text=self.text,
            background=self.bg_color,
            foreground=self.fg_color,
            relief=tk.SOLID,
            borderwidth=1,
            font=self.font,
        )
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
