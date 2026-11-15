"""
ui.py - Stand-in for Pransu's UI Module (Section 4 Contract)
Provides:
  build_window() -> (window, face, frames)
  where frames is a dictionary: {'sensors': frame, 'chat': frame, 'settings': frame}
  or unpacked as (window, face, sensors_frame, chat_frame, settings_frame).
"""

from face import Face

try:
    import tkinter as tk
except ImportError:
    tk = None


def build_window():
    """
    Builds the main Smart Desk Buddy UI window per Section 4 Contract.

    Returns:
        tuple: (window, face, frames_dict)
        where frames_dict contains:
          - 'sensors': empty frame to be filled by sensors.py
          - 'chat': empty frame to be filled by assistant.py
          - 'settings': empty frame to be filled by settings.py
    """
    if tk is None:
        # Fallback dummy objects for non-GUI environments
        class DummyWidget:
            def __init__(self, name=""):
                self.name = name

            def cget(self, k):
                return "#2d2d2d"

            def pack(self, **kwargs):
                pass

            def bind(self, *args, **kwargs):
                pass

            def winfo_toplevel(self):
                return self

            def mainloop(self):
                pass

        dummy_win = DummyWidget("window")
        dummy_face = Face()
        dummy_frames = {
            "sensors": DummyWidget("sensors"),
            "chat": DummyWidget("chat"),
            "settings": DummyWidget("settings"),
        }
        return dummy_win, dummy_face, dummy_frames

    window = tk.Tk()
    window.title("Smart Desk Buddy - HCI Project")
    window.geometry("920x760")
    window.configure(bg="#121212")

    # Top Section: Face Canvas
    top_container = tk.Frame(window, bg="#121212")
    top_container.pack(fill="x", padx=12, pady=(8, 4))

    canvas = tk.Canvas(
        top_container,
        width=300,
        height=140,
        bg="#0d1117",
        highlightthickness=2,
        highlightbackground="#30363d",
    )
    canvas.pack(pady=4)

    # Speech Bubble under the face
    bubble_frame = tk.Frame(top_container, bg="#1f2428", bd=1, relief="ridge")
    bubble_frame.pack(fill="x", padx=40, pady=4)

    bubble_label = tk.Label(
        bubble_frame,
        text="Hello! I'm your Smart Desk Buddy.",
        font=("Helvetica", 10, "italic"),
        fg="#e6edf3",
        bg="#1f2428",
        pady=6,
    )
    bubble_label.pack()

    # Timer Label
    timer_label = tk.Label(
        top_container,
        text="Timer: Idle",
        font=("Helvetica", 11, "bold"),
        fg="#ffca28",
        bg="#121212",
        pady=2,
    )
    timer_label.pack()

    # Face instance
    face_instance = Face(canvas=canvas, speech_label=bubble_label, window=window)

    # Bottom Section: Three empty frames per contract
    bottom_container = tk.Frame(window, bg="#121212")
    bottom_container.pack(fill="both", expand=True, padx=12, pady=8)

    sensors_frame = tk.Frame(bottom_container, bg="#1c2128", bd=1, relief="ridge", width=280)
    sensors_frame.pack(side="left", fill="both", expand=True, padx=4)

    chat_frame = tk.Frame(bottom_container, bg="#1c2128", bd=1, relief="ridge")
    chat_frame.pack(side="left", fill="both", expand=True, padx=4)

    settings_frame = tk.Frame(bottom_container, bg="#1c2128", bd=1, relief="ridge", width=280)
    settings_frame.pack(side="left", fill="both", expand=True, padx=4)

    frames = {
        "sensors": sensors_frame,
        "chat": chat_frame,
        "settings": settings_frame,
    }

    return window, face_instance, frames
