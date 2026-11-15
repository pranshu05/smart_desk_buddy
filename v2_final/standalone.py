"""
standalone.py - Standalone Brain Test Harness (Phase 1)
Allows Pranshu to run and demo the Brain (engine, sensors, assistant, settings, rules)
without needing Pransu's ui.py, face.py, or summary.py.

Includes:
- FakeFace class printing set_emotion() and say() to the console per PDF Section 5.
- Complete standalone UI with the three contract frames: sensors, chat, settings.
- Timer countdown display and session lifecycle controls.
- Interactive CLI mode fallback for headless environments.
"""

import sys
from typing import List, Tuple

import assistant
from engine import Engine
import rules
import sensors
import settings

try:
    import tkinter as tk
    from tkinter import messagebox
    HAS_TK = True
except ImportError:
    HAS_TK = False


class FakeFace:
    """
    Stand-in for Pransu's face.py per PDF Section 5 Step 2:
    'A tiny class with set_emotion() and say() that just prints to the console.'
    """

    def __init__(self, emotion_label=None, speech_label=None):
        self.current_emotion = "idle"
        self.last_speech = ""
        self.emotion_label = emotion_label
        self.speech_label = speech_label

    def set_emotion(self, name: str) -> None:
        self.current_emotion = name
        print(f"[CONSOLE FAKE FACE] Emotion -> {name.upper()}")
        if self.emotion_label and hasattr(self.emotion_label, "config"):
            self.emotion_label.config(text=f"Current Mood: {name.upper()}")

    def say(self, text: str) -> None:
        self.last_speech = text
        print(f'[CONSOLE FAKE FACE] Say -> "{text}"')
        if self.speech_label and hasattr(self.speech_label, "config"):
            self.speech_label.config(text=f'"{text}"')


def format_summary_text(log: List[Tuple[int, str]]) -> str:
    """Creates a neutral, non-judgmental timeline text per Section 6."""
    if not log:
        return "No events recorded during this session."

    lines = ["=== End of Session Summary ===", "Interruption Timeline:"]
    counts = {}
    minutes_with_breaks = []
    for minute, event in log:
        lines.append(f"  • Minute {minute:02d}: {event}")
        counts[event] = counts.get(event, 0) + 1
        if event in ("FIDGET", "SEAT_LEAVE", "TAB_SWITCH", "PHONE"):
            minutes_with_breaks.append(minute)

    lines.append("\nEvent Totals:")
    for ev, c in counts.items():
        lines.append(f"  - {ev}: {c}")

    if minutes_with_breaks:
        min_m, max_m = min(minutes_with_breaks), max(minutes_with_breaks)
        if min_m == max_m:
            neutral = f"Focus dipped around minute {min_m}."
        else:
            neutral = f"Focus dipped most around minute {min_m} to {max_m}."
    else:
        neutral = "Sustained uninterrupted focus throughout the entire session!"

    lines.append(f"\nObservation: {neutral}")
    lines.append("No scores and no blame — pattern visibility for self-reflection.")
    return "\n".join(lines)


def standalone_summary_display(log: List[Tuple[int, str]]):
    """Fallback summary display for standalone mode."""
    summary_text = format_summary_text(log)
    print("\n" + summary_text + "\n")
    if HAS_TK:
        try:
            top = tk.Toplevel()
            top.title("Smart Desk Buddy - End of Session Summary")
            top.geometry("450x380")
            top.configure(bg="#1e1e1e")

            lbl = tk.Label(
                top,
                text="Session Summary (Non-Judgmental Timeline)",
                font=("Helvetica", 12, "bold"),
                fg="#80cbc4",
                bg="#1e1e1e",
                pady=10,
            )
            lbl.pack()

            txt = tk.Text(
                top,
                wrap="word",
                font=("Courier", 10),
                bg="#2d2d2d",
                fg="#ffffff",
                padx=10,
                pady=10,
            )
            txt.pack(fill="both", expand=True, padx=12, pady=8)
            txt.insert("end", summary_text)
            txt.config(state="disabled")

            btn = tk.Button(
                top,
                text="Close",
                command=top.destroy,
                font=("Helvetica", 10, "bold"),
                bg="#37474f",
                fg="#ffffff",
            )
            btn.pack(pady=8)
        except Exception:
            pass


def run_standalone_gui():
    """Runs the full standalone Tkinter desktop GUI."""
    root = tk.Tk()
    root.title("Smart Desk Buddy - Brain Standalone Demo (Phase 1)")
    root.geometry("860x720")
    root.configure(bg="#1e1e1e")

    # Header Panel: Fake Face and Timer
    top_panel = tk.Frame(root, bg="#263238", bd=2, relief="groove")
    top_panel.pack(fill="x", padx=10, pady=8)

    title_lbl = tk.Label(
        top_panel,
        text="Smart Desk Buddy [Standalone Brain Demo]",
        font=("Helvetica", 13, "bold"),
        fg="#ffffff",
        bg="#263238",
    )
    title_lbl.pack(anchor="w", padx=10, pady=(6, 2))

    # Face display labels (Stand-in for Pransu's canvas)
    face_frame = tk.Frame(top_panel, bg="#1e1e1e", bd=1, relief="sunken")
    face_frame.pack(fill="x", padx=10, pady=4)

    emotion_lbl = tk.Label(
        face_frame,
        text="Current Mood: IDLE",
        font=("Helvetica", 12, "bold"),
        fg="#80d8ff",
        bg="#1e1e1e",
        pady=4,
    )
    emotion_lbl.pack()

    speech_lbl = tk.Label(
        face_frame,
        text='Buddy says: "(Waiting for focus session...)"',
        font=("Helvetica", 10, "italic"),
        fg="#b9f6ca",
        bg="#1e1e1e",
        pady=4,
    )
    speech_lbl.pack()

    # Timer & Session Controls
    timer_frame = tk.Frame(top_panel, bg="#263238")
    timer_frame.pack(fill="x", padx=10, pady=(4, 8))

    timer_lbl = tk.Label(
        timer_frame,
        text="Timer: Idle (25:00)",
        font=("Helvetica", 12, "bold"),
        fg="#ffca28",
        bg="#263238",
    )
    timer_lbl.pack(side="left")

    fake_face = FakeFace(emotion_label=emotion_lbl, speech_label=speech_lbl)
    engine = Engine(
        face=fake_face,
        summary_callback=standalone_summary_display,
        tk_root=root,
    )

    def update_timer_ui(rem_sec, state):
        mins = rem_sec // 60
        secs = rem_sec % 60
        timer_lbl.config(text=f"Timer [{state.upper()}]: {mins:02d}:{secs:02d}")

    engine.add_timer_listener(update_timer_ui)

    btn_start = tk.Button(
        timer_frame,
        text="Start Focus",
        command=engine.start_focus,
        bg="#2e7d32",
        fg="#ffffff",
        font=("Helvetica", 9, "bold"),
        padx=8,
    )
    btn_start.pack(side="right", padx=4)

    btn_break = tk.Button(
        timer_frame,
        text="Take Break Now",
        command=engine.take_break,
        bg="#f57f17",
        fg="#ffffff",
        font=("Helvetica", 9, "bold"),
        padx=8,
    )
    btn_break.pack(side="right", padx=4)

    btn_end = tk.Button(
        timer_frame,
        text="End & Summary",
        command=engine.end_session_and_show_summary,
        bg="#c62828",
        fg="#ffffff",
        font=("Helvetica", 9, "bold"),
        padx=8,
    )
    btn_end.pack(side="right", padx=4)

    # Main Body: The Three Shared Contract Frames
    body = tk.Frame(root, bg="#1e1e1e")
    body.pack(fill="both", expand=True, padx=10, pady=4)

    # Frame 1: Sensors (Left column)
    sensors_frame = tk.Frame(body, bg="#2d2d2d", bd=1, relief="ridge", width=260)
    sensors_frame.pack(side="left", fill="both", expand=True, padx=4, pady=4)

    # Frame 2: Chat Assistant (Middle column)
    chat_frame = tk.Frame(body, bg="#2d2d2d", bd=1, relief="ridge")
    chat_frame.pack(side="left", fill="both", expand=True, padx=4, pady=4)

    # Frame 3: Settings (Right column)
    settings_frame = tk.Frame(body, bg="#2d2d2d", bd=1, relief="ridge", width=260)
    settings_frame.pack(side="left", fill="both", expand=True, padx=4, pady=4)

    # Populate the frames using our modules
    sensors.setup_sensors(sensors_frame, engine, root=root)
    assistant.setup_chat(chat_frame, engine)
    settings.setup_settings(settings_frame, engine)

    print("=== Smart Desk Buddy Standalone Brain (Phase 1) Started ===")
    print("Press buttons or shortcuts [f, l, r, t, p] to simulate sensor events.")
    print("Type 'Hi ESP' in chat to interact with the Buddy.")
    root.mainloop()


def run_standalone_cli():
    """CLI test harness for environments without Tkinter or GUI display."""
    fake_face = FakeFace()
    engine = Engine(face=fake_face, summary_callback=standalone_summary_display)
    brain = assistant.AssistantBrain(engine)

    print("==========================================================")
    print(" Smart Desk Buddy - Standalone Brain Console Test Harness ")
    print("==========================================================")
    print("Available Commands:")
    print("  start         - Start focus session (SESSION_START)")
    print("  break         - Request break now (BREAK_REQUEST)")
    print("  fidget        - Simulate fidgeting (FIDGET)")
    print("  leave         - Simulate leaving seat (SEAT_LEAVE)")
    print("  return        - Simulate returning to seat (SEAT_RETURN)")
    print("  tab           - Simulate tab switch (TAB_SWITCH)")
    print("  phone         - Simulate picking up phone (PHONE)")
    print("  chat <msg>    - Send message to assistant (e.g. 'chat Hi ESP')")
    print("  strict <mode> - Set strictness: Silent | Gentle | Cheeky")
    print("  toggle <sns>  - Toggle sensor: motion | tab_switch | phone")
    print("  demo <on/off> - Toggle demo mode (60s focus / 15s break)")
    print("  tick <N>      - Advance timer by N seconds")
    print("  summary       - Show current session event log & summary")
    print("  quit          - Exit")
    print("==========================================================")

    while True:
        try:
            line = input("\n[buddy-brain] > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not line:
            continue

        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "quit" or cmd == "exit":
            break
        elif cmd == "start":
            engine.start_focus()
        elif cmd == "break":
            engine.take_break()
        elif cmd == "fidget":
            engine.handle_event("FIDGET")
        elif cmd == "leave":
            engine.handle_event("SEAT_LEAVE")
        elif cmd == "return":
            engine.handle_event("SEAT_RETURN")
        elif cmd == "tab":
            engine.handle_event("TAB_SWITCH")
        elif cmd == "phone":
            engine.handle_event("PHONE")
        elif cmd == "chat":
            reply = brain.process_message(arg)
            print(f"[CHAT REPLY] Buddy: {reply}")
        elif cmd == "strict":
            target = arg.capitalize()
            if target in rules.STRICTNESS_LEVELS:
                engine.set_strictness(target)
                print(f"Strictness set to: {target}")
            else:
                print(f"Unknown level. Choose from: {rules.STRICTNESS_LEVELS}")
        elif cmd == "toggle":
            sns = arg.lower()
            if sns in engine.sensor_switches:
                curr = engine.is_sensor_enabled(sns)
                engine.set_sensor_enabled(sns, not curr)
                print(f"Sensor '{sns}' is now {'ENABLED' if not curr else 'DISABLED'}")
            else:
                print("Choose from: motion, tab_switch, phone")
        elif cmd == "demo":
            on = arg.lower() in ("on", "true", "1", "yes")
            engine.set_demo_mode(on)
            print(f"Demo mode {'ON' if on else 'OFF'}")
        elif cmd == "tick":
            steps = int(arg) if arg.isdigit() else 1
            for _ in range(steps):
                engine.tick()
            print(f"Advanced {steps}s. State: {engine.state}, Rem: {engine.remaining_seconds}s")
        elif cmd == "summary":
            standalone_summary_display(engine.get_event_log())
        else:
            print("Unknown command. Type 'start', 'break', 'fidget', 'chat Hi ESP', or 'summary'.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_standalone_cli()
    elif HAS_TK:
        try:
            run_standalone_gui()
        except Exception as e:
            print(f"Could not open graphical display ({e}). Falling back to CLI mode...")
            run_standalone_cli()
    else:
        print("Tkinter not installed in this environment. Running CLI mode...")
        run_standalone_cli()
