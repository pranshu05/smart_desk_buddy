"""
engine.py - Smart Desk Buddy Brain Engine
Manages focus timer, session lifecycle, sensor event routing, reaction dispatch,
event logging, strictness levels, sensor toggles, and optional text-to-speech.

Shared Contract (Section 4):
- Engine receives events: SESSION_START, SEAT_LEAVE, SEAT_RETURN, FIDGET,
  TAB_SWITCH, PHONE, BREAK_REQUEST
- Decides reaction using shared word lists and rules.py
- Calls face.set_emotion(name) and face.say(text)
- Maintains event log as a list of (minute, event_name) pairs for summary screen
"""

import math
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple

import rules

# Try importing pyttsx3 for optional speech; gracefully fallback if missing
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False


class Engine:
    """
    Central Brain for the Smart Desk Buddy.
    Controls state, timers, sensor event filtering, rules dispatch, and logging.
    """

    def __init__(
        self,
        face: Any,
        summary_callback: Optional[Callable[[List[Tuple[int, str]]], None]] = None,
        tk_root: Any = None,
    ):
        """
        Args:
            face: Object providing face.set_emotion(name) and face.say(text)
            summary_callback: Optional callback show_summary(log)
            tk_root: Optional Tk root for non-blocking Tkinter timer scheduling
        """
        self.face = face
        self.summary_callback = summary_callback
        self.tk_root = tk_root

        # Session State: 'idle', 'focus', 'break'
        self.state = "idle"

        # Timer configurations (in seconds)
        self.demo_mode = False
        self.focus_duration = 25 * 60  # 25 minutes default
        self.break_duration = 5 * 60   # 5 minutes default
        self.remaining_seconds = 0
        self.elapsed_seconds = 0
        self.timer_running = False
        self._timer_job = None

        # Event log: list of (minute, event_name) pairs per Section 4 contract
        self.event_log: List[Tuple[int, str]] = []

        # Strictness level: 'Silent', 'Gentle' (default), 'Cheeky'
        self.strictness = "Gentle"

        # Sensor on/off switches (effective immediately)
        self.sensor_switches: Dict[str, bool] = {
            "motion": True,       # controls FIDGET, SEAT_LEAVE, SEAT_RETURN
            "tab_switch": True,   # controls TAB_SWITCH
            "phone": True,        # controls PHONE
        }

        # TTS Sound toggle
        self.tts_enabled = False
        self._tts_lock = threading.Lock()

        # Session tracking
        self.fidget_count = 0

        # UI listeners for timer tick updates
        self._timer_listeners: List[Callable[[int, str], None]] = []

    # -------------------------------------------------------------------------
    # Settings & Configuration (effective immediately)
    # -------------------------------------------------------------------------
    def set_strictness(self, level: str) -> None:
        """Set strictness: 'Silent', 'Gentle', or 'Cheeky'."""
        if level in rules.STRICTNESS_LEVELS:
            self.strictness = level

    def set_sensor_enabled(self, sensor_key: str, enabled: bool) -> None:
        """Enable or disable a sensor ('motion', 'tab_switch', 'phone')."""
        if sensor_key in self.sensor_switches:
            self.sensor_switches[sensor_key] = bool(enabled)

    def is_sensor_enabled(self, sensor_key: str) -> bool:
        """Check if a sensor is currently enabled."""
        return self.sensor_switches.get(sensor_key, True)

    def set_tts_enabled(self, enabled: bool) -> None:
        """Enable or disable spoken voice via pyttsx3."""
        self.tts_enabled = bool(enabled)

    def set_demo_mode(self, enabled: bool) -> None:
        """
        Toggle demo mode (60s focus, 15s break) vs normal (25m focus, 5m break).
        Adjusts active timer if in idle state.
        """
        self.demo_mode = bool(enabled)
        if self.demo_mode:
            self.focus_duration = 60
            self.break_duration = 15
        else:
            self.focus_duration = 25 * 60
            self.break_duration = 5 * 60

        if self.state == "idle":
            self.remaining_seconds = self.focus_duration
            self._notify_timer()

    def add_timer_listener(self, callback: Callable[[int, str], None]) -> None:
        """Register a callback for timer updates: callback(remaining_seconds, state)."""
        self._timer_listeners.append(callback)

    def _notify_timer(self) -> None:
        """Notify all listeners of current timer status."""
        for cb in self._timer_listeners:
            try:
                cb(self.remaining_seconds, self.state)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Event Log
    # -------------------------------------------------------------------------
    def get_event_log(self) -> List[Tuple[int, str]]:
        """Return the event log list of (minute, event_name) pairs."""
        return list(self.event_log)

    def _get_current_minute(self) -> int:
        """
        Calculate current minute offset for the event log.
        In normal mode: integer minutes elapsed (1, 2, ...).
        In demo mode: scaled to a 25-minute equivalent so presentations show
        realistic distribution (e.g. minute 1 to 25).
        """
        if self.demo_mode:
            fraction = min(1.0, max(0.0, self.elapsed_seconds / max(1, self.focus_duration)))
            return max(1, int(fraction * 25))
        else:
            return max(1, (self.elapsed_seconds // 60) + 1)

    def _get_remaining_minutes(self) -> int:
        """Calculate minutes remaining for spoken lines."""
        if self.demo_mode:
            fraction = max(0.0, self.remaining_seconds / max(1, self.focus_duration))
            return max(1, math.ceil(fraction * 25))
        else:
            return max(1, math.ceil(self.remaining_seconds / 60))

    # -------------------------------------------------------------------------
    # Event Dispatching & Sensor Handling
    # -------------------------------------------------------------------------
    def handle_event(self, event_name: str) -> None:
        """
        Receives an event from sensors, assistant, or timer.
        Filters disabled sensors, decides reaction, updates log and calls face.
        """
        # Sensor filtering: check if sensor is turned off in settings
        if event_name in ("FIDGET", "SEAT_LEAVE", "SEAT_RETURN") and not self.sensor_switches.get("motion", True):
            return
        if event_name == "TAB_SWITCH" and not self.sensor_switches.get("tab_switch", True):
            return
        if event_name == "PHONE" and not self.sensor_switches.get("phone", True):
            return

        # Special handling for BREAK_REQUEST (User Control & Freedom)
        if event_name == "BREAK_REQUEST":
            current_min = self._get_current_minute() if self.state == "focus" else 1
            self.event_log.append((current_min, event_name))
            self._execute_break_request()
            return

        # Special handling for SESSION_START
        if event_name == "SESSION_START":
            self.start_focus()
            return

        # Only react to distractions during active focus session
        if self.state != "focus":
            # During break: rules state Buddy never reacts to movement
            if self.state == "break":
                rem_min = self._get_remaining_minutes()
                emotion, text = rules.get_reaction(
                    event_name,
                    strictness=self.strictness,
                    state=self.state,
                    fidget_count=self.fidget_count,
                    remaining_minutes=rem_min,
                )
                if emotion:
                    self.face.set_emotion(emotion)
                if text and self.strictness != "Silent":
                    self.face.say(text)
                    self._speak(text)
            return

        # Increment fidget count during focus
        if event_name == "FIDGET":
            self.fidget_count += 1

        # Record in event log: (minute, event_name)
        current_min = self._get_current_minute()
        self.event_log.append((current_min, event_name))

        # Query reaction rules
        rem_min = self._get_remaining_minutes()
        emotion, text = rules.get_reaction(
            event=event_name,
            strictness=self.strictness,
            state=self.state,
            fidget_count=self.fidget_count,
            remaining_minutes=rem_min,
        )

        # Dispatch to Face
        if emotion:
            self.face.set_emotion(emotion)
        if text and self.strictness != "Silent":
            self.face.say(text)
            self._speak(text)

    # -------------------------------------------------------------------------
    # Session & Timer Lifecycle
    # -------------------------------------------------------------------------
    def start_focus(self) -> None:
        """Start a focus session: idle -> focus."""
        self._stop_timer()
        self.state = "focus"
        self.fidget_count = 0
        self.event_log = []
        self.elapsed_seconds = 0
        self.remaining_seconds = self.focus_duration
        self.timer_running = True

        # Log session start
        self.event_log.append((1, "SESSION_START"))

        # Reaction for session start
        emotion, text = rules.get_reaction(
            "SESSION_START",
            strictness=self.strictness,
            state=self.state,
            fidget_count=self.fidget_count,
            remaining_minutes=self._get_remaining_minutes(),
        )
        if emotion:
            self.face.set_emotion(emotion)
        if text and self.strictness != "Silent":
            self.face.say(text)
            self._speak(text)

        self._notify_timer()
        self._schedule_next_tick()

    def _execute_break_request(self) -> None:
        """Always granted: transitions to break."""
        emotion, text = rules.get_reaction(
            "BREAK_REQUEST",
            strictness=self.strictness,
            state=self.state,
            fidget_count=self.fidget_count,
            remaining_minutes=self._get_remaining_minutes(),
        )
        self.state = "break"
        self.remaining_seconds = self.break_duration
        self.timer_running = True

        if emotion:
            self.face.set_emotion(emotion)
        if text and self.strictness != "Silent":
            self.face.say(text)
            self._speak(text)

        self._notify_timer()
        self._schedule_next_tick()

    def take_break(self) -> None:
        """Explicit call to take break now."""
        self.handle_event("BREAK_REQUEST")

    def end_session_and_show_summary(self) -> None:
        """End session and trigger summary screen."""
        self._stop_timer()
        self.state = "idle"
        self.remaining_seconds = self.focus_duration
        self.face.set_emotion("idle")
        self._notify_timer()

        if self.summary_callback:
            self.summary_callback(self.get_event_log())

    def _on_focus_complete(self) -> None:
        """Called when focus timer reaches zero."""
        self.state = "break"
        self.remaining_seconds = self.break_duration
        self.face.set_emotion("happy")
        msg = "Focus session complete! Time for a short break."
        self.face.say(msg)
        self._speak(msg)
        self._notify_timer()
        self._schedule_next_tick()

    def _on_break_complete(self) -> None:
        """Called when break timer reaches zero."""
        self.state = "idle"
        self.remaining_seconds = self.focus_duration
        self.face.set_emotion("sleepy")
        msg = "Break is finished. Ready for another session?"
        self.face.say(msg)
        self._speak(msg)
        self._notify_timer()

        # Trigger summary at the end of full cycle
        if self.summary_callback:
            self.summary_callback(self.get_event_log())

    # -------------------------------------------------------------------------
    # Timer Tick Loop (Non-blocking with Tkinter after() or manual tick)
    # -------------------------------------------------------------------------
    def tick(self) -> None:
        """Perform one 1-second timer step."""
        if not self.timer_running:
            return

        self.elapsed_seconds += 1
        self.remaining_seconds -= 1
        self._notify_timer()

        if self.remaining_seconds <= 0:
            if self.state == "focus":
                self._on_focus_complete()
            elif self.state == "break":
                self._on_break_complete()

    def _schedule_next_tick(self) -> None:
        """Schedule the next 1s tick using tk_root.after() if available."""
        if not self.timer_running:
            return
        if self.tk_root is not None and hasattr(self.tk_root, "after"):
            self._timer_job = self.tk_root.after(1000, self._tk_tick_handler)

    def _tk_tick_handler(self) -> None:
        """Callback invoked by tk_root.after()."""
        if self.timer_running:
            self.tick()
            if self.timer_running:
                self._schedule_next_tick()

    def _stop_timer(self) -> None:
        """Cancel scheduled timer jobs."""
        self.timer_running = False
        if self._timer_job and self.tk_root is not None and hasattr(self.tk_root, "after_cancel"):
            try:
                self.tk_root.after_cancel(self._timer_job)
            except Exception:
                pass
            self._timer_job = None

    # -------------------------------------------------------------------------
    # Optional Text-to-Speech
    # -------------------------------------------------------------------------
    def _speak(self, text: str) -> None:
        """Asynchronously speak text if TTS toggle is active."""
        if not self.tts_enabled or not HAS_PYTTSX3 or not text:
            return

        # Avoid double-speaking if face already has its own active voice worker
        if hasattr(self.face, "_voice") and getattr(getattr(self.face, "_voice", None), "enabled", False):
            return

        def run_speech():
            with self._tts_lock:
                try:
                    engine = pyttsx3.init()
                    engine.setProperty("rate", 160)
                    engine.say(text)
                    engine.runAndWait()
                except Exception:
                    pass

        threading.Thread(target=run_speech, daemon=True).start()
