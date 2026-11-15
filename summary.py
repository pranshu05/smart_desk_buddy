"""
summary.py - Stand-in for Pransu's Summary Screen Module (Section 4 Contract)
Provides:
  show_summary(log)

HCI Principles:
- Non-judgmental feedback: shows interruption timeline, count for each kind,
  and a neutral sentence. No scores and no blame.
"""

from typing import List, Tuple

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    tk = None
    ttk = None


def generate_neutral_sentence(log: List[Tuple[int, str]]) -> str:
    """Computes a neutral observation sentence from the log without scores or blame."""
    interruptions = [m for m, ev in log if ev in ("FIDGET", "SEAT_LEAVE", "TAB_SWITCH", "PHONE")]
    if not interruptions:
        return "You maintained continuous focus throughout the session with zero interruptions."

    min_m = min(interruptions)
    max_m = max(interruptions)

    if len(interruptions) == 1:
        return f"Only one brief interruption occurred at minute {min_m}."
    elif min_m == max_m:
        return f"Focus dipped briefly around minute {min_m}."
    elif max_m - min_m <= 4:
        return f"Focus dipped most around minute {min_m} to {max_m}."
    else:
        return f"Interruption markers were distributed between minute {min_m} and minute {max_m}."


def show_summary(log: List[Tuple[int, str]]) -> None:
    """
    Draws the end-of-session screen from the event log.

    Args:
        log: list of (minute, event_name) pairs
    """
    sentence = generate_neutral_sentence(log)

    print("\n" + "=" * 55)
    print("         END-OF-SESSION FOCUS SUMMARY          ")
    print("=" * 55)
    print("Timeline of Events:")
    counts = {}
    for minute, ev in log:
        print(f"  [Min {minute:02d}] {ev}")
        counts[ev] = counts.get(ev, 0) + 1

    print("\nInterruption Counts:")
    for ev in ("FIDGET", "SEAT_LEAVE", "TAB_SWITCH", "PHONE"):
        print(f"  - {ev}: {counts.get(ev, 0)}")

    print(f"\nNeutral Observation:\n  \"{sentence}\"")
    print("(Non-judgmental feedback: no scores, no grades, no blame)")
    print("=" * 55 + "\n")

    if tk is None:
        return

    try:
        dialog = tk.Toplevel()
        dialog.title("Smart Desk Buddy - End of Session Summary")
        dialog.geometry("520x440")
        dialog.configure(bg="#121212")

        header = tk.Label(
            dialog,
            text="Session Summary",
            font=("Helvetica", 14, "bold"),
            fg="#80cbc4",
            bg="#121212",
            pady=10,
        )
        header.pack()

        # Canvas Timeline
        canvas = tk.Canvas(dialog, width=460, height=80, bg="#1e1e1e", highlightthickness=0)
        canvas.pack(pady=8)

        # Baseline axis (representing minutes 0 to 25)
        canvas.create_line(30, 45, 430, 45, fill="#555555", width=2)
        canvas.create_text(30, 62, text="0m", fill="#888888", font=("Helvetica", 8))
        canvas.create_text(230, 62, text="12m", fill="#888888", font=("Helvetica", 8))
        canvas.create_text(430, 62, text="25m", fill="#888888", font=("Helvetica", 8))

        color_map = {
            "FIDGET": "#3d5afe",
            "SEAT_LEAVE": "#ff9100",
            "TAB_SWITCH": "#aa00ff",
            "PHONE": "#d50000",
            "SESSION_START": "#00c853",
            "BREAK_REQUEST": "#ffca28",
        }

        # Draw markers on timeline
        for minute, ev in log:
            x = 30 + int((min(25, max(0, minute)) / 25.0) * 400)
            col = color_map.get(ev, "#ffffff")
            canvas.create_line(x, 25, x, 45, fill=col, width=3)
            canvas.create_oval(x - 4, 20, x + 4, 28, fill=col, outline="")

        # Summary text box
        txt_box = tk.Text(dialog, wrap="word", height=9, font=("Helvetica", 10), bg="#1e1e1e", fg="#e0e0e0", bd=0, padx=10, pady=8)
        txt_box.pack(fill="x", padx=24, pady=6)

        txt_box.insert("end", f"Key Finding: {sentence}\n\n", "bold")
        txt_box.insert("end", "Recorded Interruptions:\n")
        txt_box.insert("end", f"  • Fidgeting: {counts.get('FIDGET', 0)}\n")
        txt_box.insert("end", f"  • Seat departures: {counts.get('SEAT_LEAVE', 0)}\n")
        txt_box.insert("end", f"  • Tab switches: {counts.get('TAB_SWITCH', 0)}\n")
        txt_box.insert("end", f"  • Phone pickups: {counts.get('PHONE', 0)}\n")
        txt_box.config(state="disabled")

        btn = tk.Button(dialog, text="Close", command=dialog.destroy, bg="#37474f", fg="#ffffff", font=("Helvetica", 10, "bold"), padx=16, pady=4)
        btn.pack(pady=10)
    except Exception:
        pass
