"""face.py - the Desk Buddy's animated face (Pransu's part).

What it gives Pranshu's engine (the agreement in the guide, section 4):

    face.set_emotion("side_eye")      # idle focus side_eye talking happy sleepy
    face.say("Not break time yet.")   # speech bubble + the mouth moves

Two small extras so the engine can drive the little status strip above the face:

    face.set_phase("FOCUS")           # left label  (any short text)
    face.set_timer("24:59")           # right label (any short text)

And an optional voice (needs `pip install pyttsx3`; does nothing if missing):

    face.set_voice(True)              # returns False if pyttsx3 is not available

The face is drawn like a 128 x 64 OLED screen: every "pixel" is a small square
and thin black gaps between them give the lit-dot look. Everything eases
smoothly between emotions, so changing mood never snaps.
"""
import math
import os
import queue
import random
import re
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk

import theme

EMOTIONS = ("idle", "focus", "side_eye", "talking", "happy", "sleepy")

GRID_W, GRID_H = 128, 64      # the pretend OLED resolution
PIXEL = 4                     # canvas pixels per OLED square
FPS = 30
BUBBLE_H = 84                 # height of the speech-bubble area, in canvas pixels

# How each emotion looks, in OLED squares. `blink` = seconds between blinks.
# eye_w/eye_h: size of each eye   dx/dy: shift of both eyes   brow: raised brow (0 to 1)
# smile: mouth curve (0 flat, 1 big smile)   mouth_w: width of the mouth
LOOKS = {
    "idle":     dict(eye_w=24, eye_h=28, dx=0,  dy=0, brow=0.0, smile=0.25, mouth_w=16, blink=(2.5, 5.0)),
    "focus":    dict(eye_w=26, eye_h=13, dx=0,  dy=5, brow=0.0, smile=0.0,  mouth_w=12, blink=(6.0, 10.0)),
    "side_eye": dict(eye_w=24, eye_h=19, dx=12, dy=2, brow=1.0, smile=0.0,  mouth_w=12, blink=(3.0, 6.0)),
    "talking":  dict(eye_w=24, eye_h=28, dx=0,  dy=0, brow=0.0, smile=0.0,  mouth_w=18, blink=(2.0, 4.0)),
    "happy":    dict(eye_w=24, eye_h=10, dx=0,  dy=2, brow=0.0, smile=0.9,  mouth_w=24, blink=(99.0, 99.0)),
    "sleepy":   dict(eye_w=26, eye_h=5,  dx=0,  dy=7, brow=0.0, smile=0.0,  mouth_w=8,  blink=(7.0, 11.0)),
}
_EASED = ("eye_w", "eye_h", "dx", "dy", "brow", "smile", "mouth_w")

EYE_Y = 24                    # vertical centre of the eyes (OLED squares)
EYE_GAP = 26                  # each eye sits this far left/right of the centre
MOUTH_Y = 51


class _Voice:
    """Robust cross-platform voice worker.
    Uses pyttsx3 when available; automatically recovers from loop errors;
    falls back gracefully to system speech tools (aplay, spd-say, say, PowerShell).
    """

    def __init__(self):
        self.enabled = False
        self._queue = queue.Queue()
        self._thread = None
        self._engine = None
        self._engine_lock = threading.Lock()
        self._volume = 1.0
        self._rate = 160

    def enable(self, on):
        if not on:
            self.enabled = False
            return True
        self.enabled = True
        if self._thread is None:
            self._thread = threading.Thread(target=self._worker, daemon=True)
            self._thread.start()
        return True

    def set_volume(self, vol_percent):
        """Set voice volume between 0 and 100."""
        self._volume = max(0.0, min(1.0, vol_percent / 100.0))
        if self._engine:
            try:
                self._engine.setProperty("volume", self._volume)
            except Exception:
                pass

    def say(self, text):
        if self.enabled and text:
            self._queue.put(str(text))

    def _worker(self):
        # Initialize pyttsx3 engine if available
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self._rate)
            self._engine.setProperty("volume", self._volume)
        except Exception:
            self._engine = None

        while True:
            text = self._queue.get()
            self._speak_one(text)

    def _speak_one(self, text):
        # Strip emojis and non-speech symbols for clean natural synthesizer output
        clean = re.sub(r'[^\w\s.,!?\'"-]', '', text).strip()
        if not clean:
            return

        print(f'[VOICE] Speaking: "{clean}"')

        # 1. Try pyttsx3 direct
        if self._engine is not None:
            try:
                with self._engine_lock:
                    self._engine.setProperty("volume", self._volume)
                    self._engine.say(clean)
                    self._engine.runAndWait()
                return
            except Exception:
                # Reset pyttsx3 _inLoop if a runtime exception occurred
                try:
                    if getattr(self._engine, "_inLoop", False):
                        self._engine.endLoop()
                except Exception:
                    pass

        # 2. Try pyttsx3 save_to_file + custom audio player (bypasses direct pulse ALSA error)
        if self._engine is not None:
            try:
                tmp_wav = os.path.join(tempfile.gettempdir(), f"desk_buddy_{os.getpid()}.wav")
                with self._engine_lock:
                    self._engine.save_to_file(clean, tmp_wav)
                    self._engine.runAndWait()
                if os.path.exists(tmp_wav) and os.path.getsize(tmp_wav) > 0:
                    if self._play_wav(tmp_wav):
                        try:
                            os.remove(tmp_wav)
                        except Exception:
                            pass
                        return
            except Exception:
                pass

        # 3. Fallback to OS-native synthesizers
        if sys.platform.startswith("linux"):
            try:
                if subprocess.run(["spd-say", "-w", clean], timeout=8, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                    return
            except Exception:
                pass
            try:
                if subprocess.run(["espeak", clean], timeout=8, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                    return
            except Exception:
                pass
        elif sys.platform == "darwin":
            try:
                subprocess.run(["say", clean], timeout=8, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except Exception:
                pass
        elif sys.platform == "win32":
            try:
                escaped = clean.replace("'", "''")
                ps_cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{escaped}')"
                subprocess.run(["powershell", "-Command", ps_cmd], timeout=8, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except Exception:
                pass

    def _play_wav(self, wav_path):
        """Play wav file through whatever audio system is available."""
        # Try aplay default
        try:
            res = subprocess.run(["aplay", wav_path], capture_output=True, timeout=8)
            if res.returncode == 0:
                return True
        except Exception:
            pass

        # Try paplay
        try:
            res = subprocess.run(["paplay", wav_path], capture_output=True, timeout=8)
            if res.returncode == 0:
                return True
        except Exception:
            pass

        # Try discovering hardware PCM cards
        try:
            out = subprocess.run(["aplay", "-l"], capture_output=True, text=True, timeout=3).stdout
            matches = re.findall(r"card\s+(\d+):.*device\s+(\d+):", out)
            for card, dev in matches:
                res = subprocess.run(["aplay", "-D", f"plughw:{card},{dev}", wav_path], capture_output=True, timeout=8)
                if res.returncode == 0:
                    return True
        except Exception:
            pass

        return False


class Face(tk.Frame):
    """The whole face widget: status strip, OLED screen and speech bubble."""

    def __init__(self, parent, pixel=PIXEL):
        super().__init__(parent, bg=theme.BG)
        self.px = pixel
        self._cw = GRID_W * pixel
        self._ch = GRID_H * pixel

        # ---- status strip (phase on the left, timer on the right) ----------
        strip = tk.Frame(self, bg=theme.BG, width=self._cw)
        strip.pack(fill="x", pady=(0, 6))
        self._phase = tk.Label(strip, text="READY", bg=theme.BG, fg=theme.MUTED,
                               font=theme.font(11, "bold", mono=True, root=self))
        self._phase.pack(side="left")
        self._timer = tk.Label(strip, text="--:--", bg=theme.BG, fg=theme.TEXT,
                               font=theme.font(20, "bold", mono=True, root=self))
        self._timer.pack(side="right")

        # ---- the OLED screen -----------------------------------------------
        self.canvas = tk.Canvas(self, width=self._cw, height=self._ch, bg=theme.OLED_BG,
                                highlightthickness=2, highlightbackground=theme.BORDER)
        self.canvas.pack()
        self._draw_pixel_gaps()

        # ---- speech bubble -------------------------------------------------
        self.bubble = tk.Canvas(self, width=self._cw, height=BUBBLE_H, bg=theme.BG,
                                highlightthickness=0)
        self.bubble.pack(pady=(4, 0))

        # ---- state ---------------------------------------------------------
        self._emotion = "idle"
        self._cur = {k: float(LOOKS["idle"][k]) for k in _EASED}
        now = time.monotonic()
        self._blink_start = None
        self._next_blink = now + random.uniform(*LOOKS["idle"]["blink"])
        self._wander = 0.0
        self._next_wander = now + random.uniform(2.0, 4.0)
        self._speak_until = 0.0
        self._bubble_text = ""
        self._bubble_drawn = None
        self._voice = _Voice()
        self._job = None
        self._tick()

    # ------------------------------------------------------------------ API
    def set_emotion(self, name):
        """Change the mood. Unknown names are ignored (with a console warning)."""
        if name not in LOOKS:
            print(f"[face] unknown emotion {name!r}; use one of {EMOTIONS}")
            return
        self._emotion = name

    def get_emotion(self):
        return self._emotion

    def say(self, text, seconds=None):
        """Show `text` in the bubble; the mouth moves while it is shown."""
        text = str(text).strip()
        if not text:
            return
        if seconds is None:
            seconds = max(3.0, min(8.0, len(text) / 13.0))
        self._bubble_text = text
        self._speak_until = time.monotonic() + seconds
        self._voice.say(text)

    def clear(self):
        """Hide the speech bubble straight away."""
        self._speak_until = 0.0

    def set_phase(self, text):
        self._phase.config(text=str(text).upper())

    def set_timer(self, text):
        self._timer.config(text=str(text))

    def bind_engine(self, engine):
        """Show the engine's countdown and state in the status strip.

        Uses the engine's own `add_timer_listener(callback(remaining_seconds, state))`
        hook. Call it once after creating the engine:   face.bind_engine(engine)
        Without this call the Buddy still works; the strip just keeps its defaults.
        """
        names = {"idle": "READY", "focus": "FOCUS", "break": "BREAK"}

        def on_tick(remaining, state):
            if state == "idle" and not remaining:
                remaining = getattr(engine, "focus_duration", 0)
            remaining = max(0, int(remaining))
            self.set_timer(f"{remaining // 60:02d}:{remaining % 60:02d}")
            self.set_phase(names.get(state, state))

        engine.add_timer_listener(on_tick)
        on_tick(getattr(engine, "remaining_seconds", 0), getattr(engine, "state", "idle"))

    def set_voice(self, on=True):
        """Turn spoken lines on or off."""
        return self._voice.enable(bool(on))

    def set_volume(self, vol_percent):
        """Set voice volume between 0 and 100."""
        self._voice.set_volume(vol_percent)

    def destroy(self):
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None
        super().destroy()

    # ------------------------------------------------------------ animation
    def _tick(self):
        now = time.monotonic()
        self._update_state(now)
        self._draw_face(now)
        self._draw_bubble(now)
        self._job = self.after(int(1000 / FPS), self._tick)

    def _update_state(self, now):
        look = LOOKS[self._emotion]

        # ease every number a little closer to the target look
        target = dict(look)
        if self._emotion == "idle":                       # gentle looking around
            if now >= self._next_wander:
                self._wander = random.uniform(-4.0, 4.0)
                self._next_wander = now + random.uniform(2.5, 5.5)
            target["dx"] = look["dx"] + self._wander
        for k in _EASED:
            self._cur[k] += (target[k] - self._cur[k]) * 0.2

        # blinking
        if self._blink_start is None and now >= self._next_blink and self._emotion != "happy":
            self._blink_start = now
        if self._blink_start is not None and now - self._blink_start > 0.18:
            self._blink_start = None
            self._next_blink = now + random.uniform(*look["blink"])

    def _blink_factor(self, now):
        if self._blink_start is None:
            return 1.0
        u = (now - self._blink_start) / 0.18
        return 1.0 - math.sin(math.pi * min(max(u, 0.0), 1.0))

    def _mouth_open(self, now):
        talking = self._emotion == "talking" or now < self._speak_until
        if not talking:
            return 0.0
        return 0.5 + 0.5 * math.sin(now * 13.0 + 0.8 * math.sin(now * 3.1))

    # -------------------------------------------------------------- drawing
    def _draw_pixel_gaps(self):
        """Thin black lines over the screen give the lit-pixel OLED look."""
        px = self.px
        for gx in range(1, GRID_W):
            self.canvas.create_line(gx * px, 0, gx * px, self._ch, fill=theme.OLED_BG, tags="grid")
        for gy in range(1, GRID_H):
            self.canvas.create_line(0, gy * px, self._cw, gy * px, fill=theme.OLED_BG, tags="grid")

    def _chamfer(self, cx, cy, w, h, **kw):
        """A rectangle with cut corners (looks right on a pixel screen)."""
        px = self.px
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
        c = max(0.5, min(4.0, w / 2.5, h / 2.5))
        pts = [x0 + c, y0, x1 - c, y0, x1, y0 + c, x1, y1 - c,
               x1 - c, y1, x0 + c, y1, x0, y1 - c, x0, y0 + c]
        self.canvas.create_polygon([v * px for v in pts], tags="dyn", **kw)

    def _draw_face(self, now):
        c, px, p = self.canvas, self.px, self._cur
        c.delete("dyn")
        on = theme.OLED_ON
        happy = self._emotion == "happy"
        eye_h = max(1.5, p["eye_h"] * self._blink_factor(now))
        cy = EYE_Y + p["dy"]
        centres = (64 - EYE_GAP + p["dx"], 64 + EYE_GAP + p["dx"])

        for i, cx in enumerate(centres):
            if happy:
                # smiling eyes: an upside-down U
                arc_h = 9
                c.create_arc((cx - p["eye_w"] / 2) * px, (cy + 3 - arc_h) * px,
                             (cx + p["eye_w"] / 2) * px, (cy + 3 + arc_h) * px,
                             start=0, extent=180, style="arc", outline=on,
                             width=4.5 * px, tags="dyn")
            else:
                self._chamfer(cx, cy, p["eye_w"], eye_h, fill=on, outline="")
            if p["brow"] > 0.05:                         # one raised brow = "really?"
                b = p["brow"]
                top = cy - p["eye_h"] / 2
                if i == 0:
                    y1 = y2 = top - 3
                else:
                    y1, y2 = top - 3 - 2 * b, top - 3 - 6 * b
                c.create_line((cx - p["eye_w"] / 2) * px, y1 * px,
                              (cx + p["eye_w"] / 2) * px, y2 * px,
                              fill=on, width=2.4 * px, tags="dyn")

        self._draw_mouth(now)
        if self._emotion == "sleepy":
            self._draw_zzz(now)
        c.tag_raise("grid")

    def _draw_mouth(self, now):
        c, px, p = self.canvas, self.px, self._cur
        mx = 64 + p["dx"] * 0.5
        mw, s = p["mouth_w"], p["smile"]
        opened = self._mouth_open(now)
        if opened > 0.15:                                 # talking: a mouth that opens and closes
            self._chamfer(mx, MOUTH_Y + 2, mw * 0.6, 2 + 9 * opened, fill=theme.OLED_ON, outline="")
        elif s > 0.08:                                    # smile: lower half of an ellipse
            sh = mw * 0.35 * s
            c.create_arc((mx - mw / 2) * px, (MOUTH_Y - sh) * px,
                         (mx + mw / 2) * px, (MOUTH_Y + sh) * px,
                         start=180, extent=180, style="arc", outline=theme.OLED_ON,
                         width=2.6 * px, tags="dyn")
        else:                                             # flat mouth
            self._chamfer(mx, MOUTH_Y + 1, mw, 2.6, fill=theme.OLED_ON, outline="")

    def _draw_zzz(self, now):
        """Little floating z's that appear one after another when sleepy."""
        phase = (now % 3.2) / 3.2
        bob = 1.5 * math.sin(now * 1.6)
        f = theme.font(-int(self.px * 6), "bold", mono=True, root=self)
        if phase > 0.15:
            self.canvas.create_text(100 * self.px, (22 + bob) * self.px, text="z", font=f,
                                    fill=theme.OLED_DIM, tags="dyn")
        if phase > 0.45:
            f2 = theme.font(-int(self.px * 9), "bold", mono=True, root=self)
            self.canvas.create_text(111 * self.px, (11 + bob) * self.px, text="Z", font=f2,
                                    fill=theme.OLED_DIM, tags="dyn")

    # ---------------------------------------------------------- speech bubble
    def _draw_bubble(self, now):
        showing = now < self._speak_until
        key = self._bubble_text if showing else None
        if key == self._bubble_drawn:
            return
        self._bubble_drawn = key
        b = self.bubble
        b.delete("all")
        if not showing:
            return
        w, h = self._cw, BUBBLE_H
        cx = w / 2
        b.create_polygon(cx - 10, 14, cx, 3, cx + 10, 14, fill=theme.PANEL, outline=theme.BORDER)
        pts = [18, 12, w - 18, 12, w - 2, 12, w - 2, 30, w - 2, h - 18, w - 2, h - 4,
               w - 18, h - 4, 18, h - 4, 2, h - 4, 2, h - 18, 2, 30, 2, 12]
        b.create_polygon(pts, smooth=True, fill=theme.PANEL, outline=theme.BORDER)
        b.create_rectangle(cx - 9, 11, cx + 9, 13.5, fill=theme.PANEL, outline="")
        b.create_text(cx, (12 + h - 4) / 2, text=self._bubble_text, width=w - 70,
                      justify="center", fill=theme.TEXT,
                      font=theme.font(14, root=self))


# ---------------------------------------------------------------------------
# Standalone test:   python3 face.py
# Keys 1-6 change the mood, Space says a line, Q quits.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    _SAMPLE_LINES = ("Not break time yet, 14 minutes to go. Want a break now?",
                     "Welcome back.", "Almost there. Just a few more minutes.")
    _root = tk.Tk()
    _root.title("Face test")
    _root.configure(bg=theme.BG)
    _face = Face(_root)
    _face.pack(padx=24, pady=(20, 8))
    _face.set_timer("25:00")
    tk.Label(_root, bg=theme.BG, fg=theme.MUTED, font=theme.font(9, mono=True, root=_root),
             text="1 idle  2 focus  3 side-eye  4 talking  5 happy  6 sleepy\n"
                  "Space say a line   Q quit").pack(pady=(0, 16))

    def _on_key(event):
        key = event.keysym.lower()
        if len(key) == 1 and key in "123456":
            name = EMOTIONS[int(key) - 1]
            _face.set_emotion(name)
            _face.set_phase(name.replace("_", " "))
        elif key == "space":
            _face.say(random.choice(_SAMPLE_LINES))
        elif key in ("q", "escape"):
            _root.destroy()

    _root.bind("<Key>", _on_key)
    _root.mainloop()
