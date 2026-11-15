# Smart Desk Buddy — Brain Module (HCI Course Project)

This project contains **Pranshu's half (The Brain)** of the **Smart Desk Buddy** HCI course project, covering **Phase 1 (Brain)**, **Phase 3 (Connect)**, and **Phase 5 (Fixes & Report)** as outlined in the *Smart Desk Buddy – HCI Project Guide*.

The counterpart (**The Face**) is built in parallel by **Pransu** (`ui.py`, `face.py`, `summary.py`). The two halves communicate strictly through the shared contract defined in **Section 4** of the project guide.

---

## 1. Project Architecture & Contract Adherence

Per Section 4 of the project guide:
- **`build_window()`** (from `ui.py`): Returns the main window, the face controller, and three empty frames named `sensors`, `chat`, and `settings`.
- **`face.set_emotion(name)`** (from `face.py`): Updates facial expression (`idle`, `focus`, `side_eye`, `talking`, `happy`, `sleepy`).
- **`face.say(text)`** (from `face.py`): Displays text in speech bubble, moves mouth, and reverts to previous emotion after ~3 seconds.
- **`show_summary(log)`** (from `summary.py`): Displays end-of-session timeline and neutral observation sentence.
- **`engine.py`**: Receives events, logs `(minute, event_name)` pairs, decides reactions via `rules.py`, and invokes `face.set_emotion()` and `face.say()`.
- **`sensors.py`**: Populates the `sensors` frame with Wizard of Oz hardware buttons and keyboard shortcuts.
- **`assistant.py`**: Populates the `chat` frame with a conversational assistant woken by `"Hi ESP"`.
- **`settings.py`**: Populates the `settings` frame with strictness levels, sensor toggles, sound toggle, and demo mode.

---

## 2. HCI Principles Implemented (Section 11)

| Principle | Implementation in Buddy | Course Talking Point |
| :--- | :--- | :--- |
| **Visibility of system status** (Nielsen) | Face emotion and timer label continuously indicate state (`idle`, `focus`, `break`). | *"You can tell what state it is in at a glance."* |
| **User control and freedom** (Nielsen) | `"take a break now"` always works; strictness level selector; every sensor has an instant off-switch. | *"The Buddy suggests, the user decides."* |
| **Match with real world** | Human facial expressions (blinks, side-eyes) and Pomodoro rhythm. | *"People already read faces, so no manual is needed."* |
| **Minimalist, calm design** | Ambient cue, short spoken lines, non-nagging feedback. | *"An ambient signal, not another notification."* |
| **Non-judgmental feedback** | Interruption timeline shows frequency and timing with zero scores, grades, or blame. | *"It makes the pattern visible without making anyone feel monitored."* |
| **Wizard of Oz prototyping** | Physical sensor hardware is simulated through UI buttons and keyboard triggers. | *"We tested the interaction before building any hardware."* |

---

## 3. File Structure

```
smart_desk_buddy/
├── engine.py           # Core brain: focus timer (25m default/60s demo), event log, reaction dispatch
├── rules.py            # Reaction matrix: maps events + strictness to emotions and gentle lines
├── sensors.py          # Wizard of Oz buttons & shortcuts [F, L, R, T, P] in the 'sensors' frame
├── assistant.py        # Chat box in 'chat' frame: wakes on "Hi ESP", answers "how am I doing?"
├── settings.py         # Settings panel in 'settings' frame: strictness, sensor toggles, TTS, demo mode
├── standalone.py       # Phase 1 standalone demo with console FakeFace (runs without Pransu's files)
├── main.py             # Phase 3 thin integration entry point connecting to Pransu's modules
├── agreement_note.txt  # Half-page interface agreement note ready to hand to Pransu
├── test_buddy.py       # Automated test suite (unit tests & lifecycle tests)
├── face.py             # Stand-in/mock for Pransu's face module (Section 4 Contract)
├── ui.py               # Stand-in/mock for Pransu's window builder (Section 4 Contract)
├── summary.py          # Stand-in/mock for Pransu's summary screen (Section 4 Contract)
└── README.md           # Documentation and run instructions
```

---

## 4. How to Run

### Requirement
- Python 3.10+
- Built-in `tkinter` (optional text-to-speech with `pip install pyttsx3`)

### A. Run Phase 1 Standalone Demo (No partner files needed)
Run the Brain independently with the console-logging `FakeFace`:

```bash
# Graphical UI (if Tkinter / X11 display is available):
python3 standalone.py

# Terminal Console / CLI Mode (for headless or quick terminal demos):
python3 standalone.py --cli
```

In CLI mode, try:
```text
chat Hi ESP
start
fidget
leave
return
tab
phone
chat how am I doing?
break
summary
quit
```

### B. Run Phase 3 Integrated Application
Once Pransu provides `ui.py`, `face.py`, and `summary.py`, place them in the directory and run:

```bash
python3 main.py
```
*(Reference stand-in implementations of `ui.py`, `face.py`, and `summary.py` are already provided so you can run and test `main.py` right now! Swapping in Pransu's files requires zero changes to any brain files).*

### C. Run Automated Tests
Run the comprehensive test suite verifying rules, escalation, sensor filtering, timers, and assistant queries:

```bash
python3 test_buddy.py
```

---

## 5. Walkthrough of the 2-Minute Demo Script (Section 12)

Use **Demo Mode** (`60s` focus, `15s` break) for presentations:

1. **Hook (15s)**: *"Students get interrupted all the time but rarely see the pattern. Meet the Desk Buddy."*
2. **Wake it (10s)**: Type `"Hi ESP"` in the chat box. The Buddy wakes up with a friendly greeting.
3. **Start focus (10s)**: Type `"start focus"` (or click **Start Focus**). The face turns calm and focused; the timer starts.
4. **Motion (20s)**:
   - Click **Fidget [F]**: Buddy gives a quiet side-eye (no words).
   - Click **Fidget [F]** again: Buddy says *"Almost there, 25 minutes left."*
   - Click **Leave Seat [L]**: Buddy gives side-eye and says *"Not break time yet, 25 minutes to go. Want a break now?"*
5. **Digital distraction (15s)**: Click **Switch Tab [T]** or **Phone [P]**: Soft side-eye without harsh scolding.
6. **User control (10s)**: Type `"take a break now"` or click **Take Break Now**. The Buddy happily agrees: *"Break time. Your call."* Show the strictness setting in the settings panel.
7. **Summary (20s)**: When session ends, review the non-judgmental timeline and neutral observation sentence.
8. **Close (20s)**: Conclude with testing insights and user feedback.
