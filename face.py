"""
face.py - Stand-in for Pransu's Animated Face Module (Section 4 Contract)
Provides:
  face.set_emotion(name)
  face.say(text)

Emotions: idle, focus, side_eye, talking, happy, sleepy
"""

from typing import Optional

try:
    import tkinter as tk
except ImportError:
    tk = None


class Face:
    """
    Animated Face Controller satisfying the Section 4 Contract.
    Can drive a Tkinter canvas OLED representation or console output.
    """

    def __init__(self, canvas=None, speech_label=None, window=None):
        self.canvas = canvas
        self.speech_label = speech_label
        self.window = window
        self.current_emotion = "idle"
        self._previous_emotion = "idle"
        self._say_timer = None

        if self.canvas is not None:
            self._draw_face()

    def set_emotion(self, name: str) -> None:
        """Sets the active emotion: idle, focus, side_eye, talking, happy, sleepy."""
        self.current_emotion = name
        print(f"[FACE] Emotion changed to: {name}")
        if self.canvas is not None:
            self._draw_face()

    def say(self, text: str) -> None:
        """
        Shows text in the speech bubble, displays talking mouth,
        and reverts to previous mood after ~3 seconds per Section 6 Step 5.
        """
        print(f'[FACE] Speech Bubble: "{text}"')
        self._previous_emotion = self.current_emotion
        self.current_emotion = "talking"

        if self.speech_label and hasattr(self.speech_label, "config"):
            self.speech_label.config(text=f'"{text}"')

        if self.canvas is not None:
            self._draw_face()

        # Revert back after 3 seconds
        if self.window is not None and hasattr(self.window, "after"):
            if self._say_timer is not None:
                try:
                    self.window.after_cancel(self._say_timer)
                except Exception:
                    pass
            self._say_timer = self.window.after(3000, self._revert_emotion)

    def _revert_emotion(self) -> None:
        self.current_emotion = self._previous_emotion
        if self.canvas is not None:
            self._draw_face()

    def _draw_face(self) -> None:
        """Draws OLED-style face on canvas using rectangular blocks."""
        if self.canvas is None:
            return

        self.canvas.delete("all")
        w = int(self.canvas.cget("width"))
        h = int(self.canvas.cget("height"))

        # OLED background
        self.canvas.create_rectangle(0, 0, w, h, fill="#0d1117", outline="")

        emo = self.current_emotion

        # Eyes: Left and Right
        eye_color = "#00e5ff"
        if emo == "idle":
            # Normal open eyes
            self.canvas.create_rectangle(80, 45, 120, 85, fill=eye_color, outline="")
            self.canvas.create_rectangle(180, 45, 220, 85, fill=eye_color, outline="")
            # Mouth: gentle neutral line
            self.canvas.create_rectangle(135, 105, 165, 110, fill=eye_color, outline="")
        elif emo == "focus":
            # Half-closed, calm
            self.canvas.create_rectangle(80, 58, 120, 80, fill=eye_color, outline="")
            self.canvas.create_rectangle(180, 58, 220, 80, fill=eye_color, outline="")
            # Calm flat mouth
            self.canvas.create_rectangle(135, 105, 165, 109, fill=eye_color, outline="")
        elif emo == "side_eye":
            # Pupils shifted to one side, one brow raised
            self.canvas.create_rectangle(80, 48, 105, 85, fill=eye_color, outline="")
            self.canvas.create_rectangle(180, 48, 205, 85, fill=eye_color, outline="")
            # Raised eyebrow on right
            self.canvas.create_rectangle(175, 35, 225, 40, fill="#ffd600", outline="")
            # Skeptical smirk
            self.canvas.create_rectangle(130, 105, 170, 110, fill=eye_color, outline="")
        elif emo == "talking":
            # Open eyes and open mouth
            self.canvas.create_rectangle(80, 45, 120, 85, fill=eye_color, outline="")
            self.canvas.create_rectangle(180, 45, 220, 85, fill=eye_color, outline="")
            # Open rectangular mouth
            self.canvas.create_rectangle(130, 98, 170, 118, fill=eye_color, outline="")
        elif emo == "happy":
            # Upward arc smile eyes
            self.canvas.create_polygon(80, 75, 100, 50, 120, 75, fill=eye_color)
            self.canvas.create_polygon(180, 75, 200, 50, 220, 75, fill=eye_color)
            # Smile mouth
            self.canvas.create_polygon(125, 100, 150, 122, 175, 100, fill=eye_color)
        elif emo == "sleepy":
            # Low droopy eyelids
            self.canvas.create_rectangle(80, 70, 120, 85, fill=eye_color, outline="")
            self.canvas.create_rectangle(180, 70, 220, 85, fill=eye_color, outline="")
            # Relaxed small mouth
            self.canvas.create_rectangle(140, 105, 160, 108, fill=eye_color, outline="")
        else:
            # Fallback
            self.canvas.create_rectangle(80, 45, 120, 85, fill=eye_color, outline="")
            self.canvas.create_rectangle(180, 45, 220, 85, fill=eye_color, outline="")
