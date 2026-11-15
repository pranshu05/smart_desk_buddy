"""
sensors.py - Smart Desk Buddy Simulated Sensor Panel
Fills the 'sensors' frame with buttons pretending to be hardware sensors
(motion sensor, tab-switch detector, phone-pickup detector) using Wizard of Oz prototyping.

Keyboard Shortcuts:
- [F] / [f]: Fidget (FIDGET)
- [L] / [l]: Leave Seat (SEAT_LEAVE)
- [R] / [r]: Return to Seat (SEAT_RETURN)
- [T] / [t]: Switch Tab (TAB_SWITCH)
- [P] / [p]: Pick Up Phone (PHONE)
"""

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    tk = None
    ttk = None

try:
    import theme
    HAS_THEME = True
except ImportError:
    HAS_THEME = False


def setup_sensors(parent_frame, engine, root=None):
    """
    Fills the provided parent_frame with simulated sensor buttons
    and binds keyboard shortcuts.

    Args:
        parent_frame: Tkinter Frame where buttons are placed.
        engine: Engine instance that receives events.
        root: Optional top-level window for keyboard bindings.
    """
    if tk is None:
        return

    # Determine theme styling
    bg_color = theme.PANEL if HAS_THEME else (parent_frame.cget("bg") if hasattr(parent_frame, "cget") else "#2d2d2d")
    fg_title = theme.ACCENT if HAS_THEME else "#e0e0e0"
    fg_muted = theme.MUTED if HAS_THEME else "#aaaaaa"
    title_font = theme.font(10, "bold", mono=True, root=parent_frame) if HAS_THEME else ("Helvetica", 11, "bold")
    sub_font = theme.font(9, root=parent_frame) if HAS_THEME else ("Helvetica", 9)
    btn_font = theme.font(10, "bold", root=parent_frame) if HAS_THEME else ("Helvetica", 10)

    # Frame header / Section Title
    title_label = tk.Label(
        parent_frame,
        text="SIMULATED SENSORS",
        font=title_font,
        fg=fg_title,
        bg=bg_color,
        pady=2,
    )
    title_label.pack(anchor="w", padx=6, pady=(2, 1))

    subtitle = tk.Label(
        parent_frame,
        text="Buttons trigger fake sensors (shortcuts: F, L, R, T, P):",
        font=sub_font,
        fg=fg_muted,
        bg=bg_color,
    )
    subtitle.pack(anchor="w", padx=6, pady=(0, 6))

    # Button grid container
    btn_container = tk.Frame(parent_frame, bg=bg_color)
    btn_container.pack(fill="x", padx=4, pady=2)

    # Sensor definitions: (label, event_name, shortcut_key, accent_hover)
    sensor_items = [
        ("Motion: Fidget [F]", "FIDGET", "f", "#ffb454"),
        ("Motion: Leave Seat [L]", "SEAT_LEAVE", "l", "#ff7a90"),
        ("Motion: Return [R]", "SEAT_RETURN", "r", "#7ee8ff"),
        ("Digital: Switch Tab [T]", "TAB_SWITCH", "t", "#a899ff"),
        ("Phone: Pick Up [P]", "PHONE", "p", "#5eead4"),
    ]

    btn_bg = theme.BUTTON if HAS_THEME else "#3c3f41"
    btn_fg = theme.TEXT if HAS_THEME else "#ffffff"

    for label_text, event_name, key, accent_color in sensor_items:
        def make_handler(evt=event_name):
            return lambda: engine.handle_event(evt)

        btn = tk.Button(
            btn_container,
            text=label_text,
            command=make_handler(),
            font=btn_font,
            fg=btn_fg,
            bg=btn_bg,
            activebackground=accent_color,
            activeforeground="#0d1117" if HAS_THEME else "#ffffff",
            relief="flat",
            bd=1,
            padx=8,
            pady=5,
            cursor="hand2",
            anchor="w",
        )
        btn.pack(fill="x", pady=2)

    # Bind keyboard shortcuts
    top_window = root
    if top_window is None and hasattr(parent_frame, "winfo_toplevel"):
        try:
            top_window = parent_frame.winfo_toplevel()
        except Exception:
            top_window = None

    if top_window is not None:
        def bind_key(event_name, key_char):
            def handler(event):
                # Don't trigger if user is currently typing in an Entry or Text widget
                widget = event.widget
                widget_class = getattr(widget, "winfo_class", lambda: "")()
                if widget_class in ("Entry", "Text", "TEntry"):
                    return
                engine.handle_event(event_name)

            top_window.bind(f"<{key_char.lower()}>", handler)
            top_window.bind(f"<{key_char.upper()}>", handler)

        for _, event_name, key, _ in sensor_items:
            bind_key(event_name, key)
