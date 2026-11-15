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

try:
    import theme
    HAS_THEME = True
except ImportError:
    HAS_THEME = False


def setup_settings(parent_frame, engine):
    """
    Fills the provided parent_frame with settings controls.

    Args:
        parent_frame: Tkinter Frame where settings widgets are rendered.
        engine: Engine instance whose configuration is updated immediately.
    """
    if tk is None:
        return

    bg_color = theme.PANEL if HAS_THEME else (parent_frame.cget("bg") if hasattr(parent_frame, "cget") else "#2d2d2d")
    fg_title = theme.ACCENT if HAS_THEME else "#80cbc4"
    fg_text = theme.TEXT if HAS_THEME else "#ffffff"
    fg_muted = theme.MUTED if HAS_THEME else "#aaaaaa"
    title_font = theme.font(10, "bold", mono=True, root=parent_frame) if HAS_THEME else ("Helvetica", 11, "bold")
    label_font = theme.font(9, "bold", root=parent_frame) if HAS_THEME else ("Helvetica", 9, "bold")
    body_font = theme.font(9, root=parent_frame) if HAS_THEME else ("Helvetica", 9)

    # Header
    header = tk.Label(
        parent_frame,
        text="SETTINGS & CONTROLS",
        font=title_font,
        fg=fg_title,
        bg=bg_color,
        pady=2,
    )
    header.pack(anchor="w", padx=6, pady=(2, 1))

    # --- Strictness Section ---
    strict_frame = tk.LabelFrame(
        parent_frame,
        text=" Strictness ",
        font=label_font,
        fg=fg_title,
        bg=bg_color,
        bd=1,
    )
    strict_frame.pack(fill="x", padx=4, pady=2)

    strict_var = tk.StringVar(value=engine.strictness)

    def on_strictness_change():
        level = strict_var.get()
        engine.set_strictness(level)

    for level, desc in [
        ("Silent", "Silent (Face only, no spoken lines)"),
        ("Gentle", "Gentle (Default calm companion)"),
        ("Cheeky", "Cheeky (Playful, humorous lines)"),
    ]:
        rb = tk.Radiobutton(
            strict_frame,
            text=desc,
            value=level,
            variable=strict_var,
            command=on_strictness_change,
            font=body_font,
            fg=fg_text,
            bg=bg_color,
            selectcolor="#0d1117" if HAS_THEME else "#1e1e1e",
            activebackground=bg_color,
            activeforeground=fg_text,
            anchor="w",
        )
        rb.pack(anchor="w", padx=4, pady=1)

    # --- Sensor On/Off Switches Section (Effective immediately) ---
    sensor_frame = tk.LabelFrame(
        parent_frame,
        text=" Active Sensors ",
        font=label_font,
        fg=fg_title,
        bg=bg_color,
        bd=1,
    )
    sensor_frame.pack(fill="x", padx=4, pady=2)

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
        text="Motion (Fidget / Leave seat)",
        variable=motion_var,
        command=on_motion_toggle,
        font=body_font,
        fg=fg_text,
        bg=bg_color,
        selectcolor="#0d1117" if HAS_THEME else "#1e1e1e",
        activebackground=bg_color,
        activeforeground=fg_text,
        anchor="w",
    )
    chk_motion.pack(anchor="w", padx=4, pady=1)

    chk_tab = tk.Checkbutton(
        sensor_frame,
        text="Tab-Switch Detector",
        variable=tab_var,
        command=on_tab_toggle,
        font=body_font,
        fg=fg_text,
        bg=bg_color,
        selectcolor="#0d1117" if HAS_THEME else "#1e1e1e",
        activebackground=bg_color,
        activeforeground=fg_text,
        anchor="w",
    )
    chk_tab.pack(anchor="w", padx=4, pady=1)

    chk_phone = tk.Checkbutton(
        sensor_frame,
        text="Phone-Pickup Detector",
        variable=phone_var,
        command=on_phone_toggle,
        font=body_font,
        fg=fg_text,
        bg=bg_color,
        selectcolor="#0d1117" if HAS_THEME else "#1e1e1e",
        activebackground=bg_color,
        activeforeground=fg_text,
        anchor="w",
    )
    chk_phone.pack(anchor="w", padx=4, pady=1)

    # --- Mode & Voice Section ---
    system_frame = tk.LabelFrame(
        parent_frame,
        text=" Presentation & Voice ",
        font=label_font,
        fg=fg_title,
        bg=bg_color,
        bd=1,
    )
    system_frame.pack(fill="x", padx=4, pady=2)

    # Demo mode toggle (60s focus, 15s break)
    demo_var = tk.BooleanVar(value=engine.demo_mode)

    def on_demo_toggle():
        engine.set_demo_mode(demo_var.get())

    chk_demo = tk.Checkbutton(
        system_frame,
        text="Demo Mode (60s focus / 15s break)",
        variable=demo_var,
        command=on_demo_toggle,
        font=body_font,
        fg=fg_text,
        bg=bg_color,
        selectcolor="#0d1117" if HAS_THEME else "#1e1e1e",
        activebackground=bg_color,
        activeforeground=fg_text,
        anchor="w",
    )
    chk_demo.pack(anchor="w", padx=4, pady=1)

    # Sound / TTS toggle
    tts_var = tk.BooleanVar(value=engine.tts_enabled)

    def on_tts_toggle():
        engine.set_tts_enabled(tts_var.get())

    chk_tts = tk.Checkbutton(
        system_frame,
        text="Spoken Voice / TTS",
        variable=tts_var,
        command=on_tts_toggle,
        font=body_font,
        fg=fg_text,
        bg=bg_color,
        selectcolor="#0d1117" if HAS_THEME else "#1e1e1e",
        activebackground=bg_color,
        activeforeground=fg_text,
        anchor="w",
    )
    chk_tts.pack(anchor="w", padx=4, pady=1)
