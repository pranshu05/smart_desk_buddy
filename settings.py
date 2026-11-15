"""
settings.py - Smart Desk Buddy Settings Panel
Fills the 'settings' frame with controls for strictness level, sound/TTS,
individual sensor on/off switches, and demo mode.

HCI Principle:
- Nielsen: User control and freedom ("The Buddy suggests, the user decides.")
- All changes are applied immediately to the engine.
"""

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    tk = None
    ttk = None


def setup_settings(parent_frame, engine):
    """
    Fills the provided parent_frame with settings controls.

    Args:
        parent_frame: Tkinter Frame where settings widgets are rendered.
        engine: Engine instance whose configuration is updated immediately.
    """
    if tk is None:
        return

    bg_color = parent_frame.cget("bg") if hasattr(parent_frame, "cget") else "#2d2d2d"

    # Header
    header = tk.Label(
        parent_frame,
        text="Settings & User Control",
        font=("Helvetica", 11, "bold"),
        fg="#e0e0e0",
        bg=bg_color,
        pady=4,
    )
    header.pack(anchor="w", padx=8, pady=(4, 2))

    # --- Strictness Section ---
    strict_frame = tk.LabelFrame(
        parent_frame,
        text=" Strictness Level ",
        font=("Helvetica", 9, "bold"),
        fg="#80cbc4",
        bg=bg_color,
        bd=1,
    )
    strict_frame.pack(fill="x", padx=8, pady=4)

    strict_var = tk.StringVar(value=engine.strictness)

    def on_strictness_change():
        level = strict_var.get()
        engine.set_strictness(level)

    for level, desc in [
        ("Silent", "Silent (Face changes only, no words)"),
        ("Gentle", "Gentle (Default companion, never nagging)"),
        ("Cheeky", "Cheeky (Playful, humorous lines)"),
    ]:
        rb = tk.Radiobutton(
            strict_frame,
            text=desc,
            value=level,
            variable=strict_var,
            command=on_strictness_change,
            font=("Helvetica", 9),
            fg="#ffffff",
            bg=bg_color,
            selectcolor="#1e1e1e",
            activebackground=bg_color,
            activeforeground="#ffffff",
            anchor="w",
        )
        rb.pack(anchor="w", padx=6, pady=2)

    # --- Sensor On/Off Switches Section (Effective immediately) ---
    sensor_frame = tk.LabelFrame(
        parent_frame,
        text=" Active Sensors (Turn off anytime) ",
        font=("Helvetica", 9, "bold"),
        fg="#80cbc4",
        bg=bg_color,
        bd=1,
    )
    sensor_frame.pack(fill="x", padx=8, pady=4)

    motion_var = tk.BooleanVar(value=engine.is_sensor_enabled("motion"))
    tab_var = tk.BooleanVar(value=engine.is_sensor_enabled("tab_switch"))
    phone_var = tk.BooleanVar(value=engine.is_sensor_enabled("phone"))

    def on_motion_toggle():
        engine.set_sensor_enabled("motion", motion_var.get())

    def on_tab_toggle():
        engine.set_sensor_enabled("tab_switch", tab_var.get())

    def on_phone_toggle():
        engine.set_sensor_enabled("phone", phone_var.get())

    chk_motion = tk.Checkbutton(
        sensor_frame,
        text="Motion Sensor (Fidget / Leave Seat)",
        variable=motion_var,
        command=on_motion_toggle,
        font=("Helvetica", 9),
        fg="#ffffff",
        bg=bg_color,
        selectcolor="#1e1e1e",
        activebackground=bg_color,
        activeforeground="#ffffff",
        anchor="w",
    )
    chk_motion.pack(anchor="w", padx=6, pady=2)

    chk_tab = tk.Checkbutton(
        sensor_frame,
        text="Tab-Switch Detector",
        variable=tab_var,
        command=on_tab_toggle,
        font=("Helvetica", 9),
        fg="#ffffff",
        bg=bg_color,
        selectcolor="#1e1e1e",
        activebackground=bg_color,
        activeforeground="#ffffff",
        anchor="w",
    )
    chk_tab.pack(anchor="w", padx=6, pady=2)

    chk_phone = tk.Checkbutton(
        sensor_frame,
        text="Phone-Pickup Detector",
        variable=phone_var,
        command=on_phone_toggle,
        font=("Helvetica", 9),
        fg="#ffffff",
        bg=bg_color,
        selectcolor="#1e1e1e",
        activebackground=bg_color,
        activeforeground="#ffffff",
        anchor="w",
    )
    chk_phone.pack(anchor="w", padx=6, pady=2)

    # --- Mode & Voice Section ---
    system_frame = tk.LabelFrame(
        parent_frame,
        text=" Preferences & Presentation Mode ",
        font=("Helvetica", 9, "bold"),
        fg="#80cbc4",
        bg=bg_color,
        bd=1,
    )
    system_frame.pack(fill="x", padx=8, pady=4)

    # Demo mode toggle (60s focus, 15s break)
    demo_var = tk.BooleanVar(value=engine.demo_mode)

    def on_demo_toggle():
        engine.set_demo_mode(demo_var.get())

    chk_demo = tk.Checkbutton(
        system_frame,
        text="Demo Mode (60s focus, 15s break for presentations)",
        variable=demo_var,
        command=on_demo_toggle,
        font=("Helvetica", 9),
        fg="#ffffff",
        bg=bg_color,
        selectcolor="#1e1e1e",
        activebackground=bg_color,
        activeforeground="#ffffff",
        anchor="w",
    )
    chk_demo.pack(anchor="w", padx=6, pady=2)

    # Sound / TTS toggle
    tts_var = tk.BooleanVar(value=engine.tts_enabled)

    def on_tts_toggle():
        engine.set_tts_enabled(tts_var.get())

    chk_tts = tk.Checkbutton(
        system_frame,
        text="Spoken Voice / Text-to-Speech (pyttsx3)",
        variable=tts_var,
        command=on_tts_toggle,
        font=("Helvetica", 9),
        fg="#ffffff",
        bg=bg_color,
        selectcolor="#1e1e1e",
        activebackground=bg_color,
        activeforeground="#ffffff",
        anchor="w",
    )
    chk_tts.pack(anchor="w", padx=6, pady=2)
