"""ui.py - the Desk Buddy's main window (Pransu's part).

For Pranshu's main.py:

    from ui import build_window
    root, face, panels = build_window()
    # face.set_emotion(...), face.say(...), face.set_timer(...), face.set_phase(...)
    # panels["sensors"], panels["chat"], panels["settings"] are empty frames:
    #   put your own widgets in them, e.g. tk.Label(panels["chat"], ...).pack()
    root.mainloop()

To try the window on its own, just run:   python ui.py
Keys: 1-6 change the face, Space says a line, S opens the summary screen, Q quits.
"""
import random
import tkinter as tk

import theme
from face import EMOTIONS, Face

PLACEHOLDERS = {
    "sensors": "Pranshu's sensor buttons go here",
    "chat": "Pranshu's chat box goes here",
    "settings": "Pranshu's settings go here",
}

TEST_LINES = (
    "Not break time yet, 14 minutes to go. Want a break now?",
    "Welcome back.",
    "Almost there. Just a few more minutes.",
    "Break time. Your call.",
)

TEST_LOG = [(3, "FIDGET"), (7, "TAB_SWITCH"), (8, "TAB_SWITCH"), (14, "SEAT_LEAVE"),
            (18, "FIDGET"), (19, "PHONE"), (20, "TAB_SWITCH"), (21, "SEAT_LEAVE")]


def _card(parent):
    """A plain card. Returns (outer, inner); Pranshu's panel goes inside `inner`."""
    outer = tk.Frame(parent, bg=theme.PANEL, highlightthickness=1,
                     highlightbackground=theme.BORDER)
    inner = tk.Frame(outer, bg=theme.PANEL)
    inner.pack(fill="both", expand=True, padx=10, pady=8)
    return outer, inner


def build_window(placeholders=False, debug_keys=False, voice=True):
    """Create the window. Returns (root, face, panels).

    placeholders: put a grey note in each empty frame (handy when testing alone)
    debug_keys:   keys 1-6, Space, S and Q for trying things without the engine
    voice:        speak the buddy's lines aloud (needs `pip install pyttsx3`; silent if missing)
    """
    root = tk.Tk()
    root.title("Smart Desk Buddy")
    root.configure(bg=theme.BG)
    root.resizable(False, False)

    # ---- left column: the face, with the sensor buttons under it ----------
    left = tk.Frame(root, bg=theme.BG)
    left.grid(row=0, column=0, padx=(24, 12), pady=20, sticky="n")
    face = Face(left)
    face.pack()
    if debug_keys:
        tk.Label(left, bg=theme.BG, fg=theme.MUTED, font=theme.font(9, mono=True, root=root),
                 text="1 idle  2 focus  3 side-eye  4 talking  5 happy  6 sleepy\n"
                      "Space say a line   S summary   Q quit").pack(pady=(10, 0))
    # ---- right column: chat and settings ------------------------------------
    right = tk.Frame(root, bg=theme.BG)
    right.grid(row=0, column=1, padx=(12, 24), pady=20, sticky="n")
    tk.Frame(right, bg=theme.BG, width=360, height=1).pack()          # minimum column width

    # each card goes in the column that keeps the window short enough for a laptop screen
    homes = {"sensors": left, "chat": right, "settings": right}
    panels = {}
    for name in ("sensors", "chat", "settings"):
        outer, inner = _card(homes[name])
        outer.pack(fill="x", pady=(14 if name == "sensors" else 0, 12 if name == "chat" else 0))
        panels[name] = inner
        if placeholders:
            tk.Label(inner, text=PLACEHOLDERS[name], bg=theme.PANEL, fg=theme.MUTED,
                     font=theme.font(10, root=root)).pack(pady=18)

    if voice and not face.set_voice(True):
        print("Voice is off: run  pip install pyttsx3  to hear the buddy.")
    if debug_keys:
        _bind_debug_keys(root, face)
    return root, face, panels


def _bind_debug_keys(root, face):
    from summary import show_summary

    def on_key(event):
        k = event.keysym.lower()
        if k in "123456" and len(k) == 1:
            name = EMOTIONS[int(k) - 1]
            face.set_emotion(name)
            face.set_phase(name.replace("_", " "))
        elif k == "space":
            face.say(random.choice(TEST_LINES))
        elif k == "s":
            show_summary(TEST_LOG, session_length=25, parent=root)
        elif k in ("q", "escape"):
            root.destroy()

    root.bind("<Key>", on_key)


if __name__ == "__main__":
    app, _face, _panels = build_window(placeholders=True, debug_keys=True)
    _face.set_timer("25:00")
    app.mainloop()