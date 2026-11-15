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
    # Graceful stub for environments without Tkinter
    tk = None
    ttk = None


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

    # Frame header / Section Title
    title_label = tk.Label(
        parent_frame,
        text="Simulated Sensors (Wizard of Oz)",
        font=("Helvetica", 11, "bold"),
        fg="#e0e0e0",
        bg=parent_frame.cget("bg") if hasattr(parent_frame, "cget") else "#2d2d2d",
        pady=4,
    )
    title_label.pack(anchor="w", padx=8, pady=(4, 2))

    subtitle = tk.Label(
        parent_frame,
        text="Click a button or use shortcut keys to simulate sensor triggers:",
        font=("Helvetica", 9),
        fg="#aaaaaa",
        bg=parent_frame.cget("bg") if hasattr(parent_frame, "cget") else "#2d2d2d",
    )
    subtitle.pack(anchor="w", padx=8, pady=(0, 6))

    # Button grid container
    btn_container = tk.Frame(
        parent_frame,
        bg=parent_frame.cget("bg") if hasattr(parent_frame, "cget") else "#2d2d2d",
    )
    btn_container.pack(fill="x", padx=8, pady=4)

    # Sensor definitions: (label, event_name, shortcut_key, sensor_type)
    sensor_items = [
        ("Motion: Fidget [F]", "FIDGET", "f", "#3d5afe"),
        ("Motion: Leave Seat [L]", "SEAT_LEAVE", "l", "#ff9100"),
        ("Motion: Return to Seat [R]", "SEAT_RETURN", "r", "#00c853"),
        ("Digital: Switch Tab [T]", "TAB_SWITCH", "t", "#aa00ff"),
        ("Phone: Pick Up Phone [P]", "PHONE", "p", "#d50000"),
    ]

    for label_text, event_name, key, accent_color in sensor_items:
        def make_handler(evt=event_name):
            return lambda: engine.handle_event(evt)

        btn = tk.Button(
            btn_container,
            text=label_text,
            command=make_handler(),
            font=("Helvetica", 10),
            fg="#ffffff",
            bg="#3c3f41",
            activebackground=accent_color,
            activeforeground="#ffffff",
            relief="raised",
            bd=1,
            padx=8,
            pady=6,
            cursor="hand2",
        )
        btn.pack(fill="x", pady=3)

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
