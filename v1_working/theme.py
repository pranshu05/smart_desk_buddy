"""theme.py - colours and fonts shared by every screen of the Desk Buddy.

Pransu owns this file. Pranshu: import it so your sensor buttons, chat box and
settings panel match the rest of the window, e.g.

    import theme
    tk.Button(frame, text="Fidget", bg=theme.PANEL, fg=theme.TEXT,
              font=theme.font(11))
"""
import tkinter as tk
from tkinter import font as tkfont

# ---- window colours -------------------------------------------------------
BG = "#0d1117"        # window background
PANEL = "#161d27"     # buttons, inputs, cards
BORDER = "#2a3544"    # thin outlines
TEXT = "#e6edf3"      # main text
MUTED = "#8b98a9"     # secondary text
ACCENT = "#7ee8ff"    # the one accent colour (same as the lit OLED pixels)

# ---- the OLED screen ------------------------------------------------------
OLED_BG = "#000000"
OLED_ON = ACCENT
OLED_DIM = "#3b7f90"  # fainter lit pixels (for the little "z" when sleepy)

# ---- one colour per kind of interruption (summary screen) -----------------
KIND_COLORS = {
    "FIDGET": "#ffb454",
    "SEAT_LEAVE": "#ff7a90",
    "TAB_SWITCH": "#a899ff",
    "PHONE": "#5eead4",
}

BUTTON = "#243040"
BUTTON_HOVER = "#2f3d52"

_family_cache = {}


def _pick(root, candidates, fallback):
    """First font family from `candidates` that exists on this computer."""
    key = tuple(candidates)
    if key not in _family_cache:
        available = set(tkfont.families(root))
        _family_cache[key] = next((c for c in candidates if c in available), fallback)
    return _family_cache[key]


def font(size=11, weight="normal", mono=False, root=None):
    """A Tk font tuple that looks decent on Windows, macOS and Linux."""
    if mono:
        family = _pick(root, ("Consolas", "Menlo", "DejaVu Sans Mono", "Courier New"), "Courier")
    else:
        family = _pick(root, ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter",
                              "DejaVu Sans", "Arial"), "Helvetica")
    return (family, size, weight)


def button(parent, text, command, accent=False):
    """A flat, coloured button that looks the same on Windows, macOS and Linux.

    (Built from a Label because the native Tk Button ignores colours on macOS.)
    Returns the widget; you still call .pack() / .grid() on it.
    """
    bg, hover = (ACCENT, "#a6f0ff") if accent else (BUTTON, BUTTON_HOVER)
    fg = "#04222b" if accent else TEXT
    b = tk.Label(parent, text=text, bg=bg, fg=fg, padx=14, pady=7, cursor="hand2",
                 font=font(11, "bold", root=parent))
    b.bind("<Enter>", lambda _e: b.config(bg=hover))
    b.bind("<Leave>", lambda _e: b.config(bg=bg))
    b.bind("<ButtonRelease-1>", lambda _e: command())
    return b
