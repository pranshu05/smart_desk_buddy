# Smart Desk Buddy — Brain & Integrated Application (HCI Course Project)

This repository contains the complete working software prototype for the **Smart Desk Buddy** HCI course project, combining **Pranshu's half (The Brain)** and **Pransu's half (The Face)** according to the *Smart Desk Buddy – HCI Project Guide*.

---

## 1. Project Architecture & Contract Adherence

Per Section 4 of the project guide, the two halves connect seamlessly through the contract:
- **`ui.build_window()`**: Returns the main window, the animated face controller, and three empty card frames: `sensors`, `chat`, and `settings`.
- **`face.set_emotion(name)`**: Updates the OLED face expression (`idle`, `focus`, `side_eye`, `talking`, `happy`, `sleepy`).
- **`face.say(text)`**: Displays text in the speech bubble, animates mouth movement, and reverts to the previous mood after ~3 seconds.
- **`face.bind_engine(engine)`**: Live status strip integration showing the phase (`READY`, `FOCUS`, `BREAK`) and timer countdown (`24:59`).
- **`summary.show_summary(log)`**: Draws an end-of-session interruption timeline and neutral observation sentence.
- **`engine.py`**: Focus timer (25 min default / 60s demo), event log `[(minute, event_name)]`, reaction dispatch, and immediate sensor filtering.
- **`sensors.py`**: Wizard of Oz hardware buttons and keyboard shortcuts `[F, L, R, T, P]`.
- **`assistant.py`**: Chat box in `chat` frame: wakes on `"Hi ESP"`, answers `"how am I doing?"` using `summary.summarize(log)`.
- **`settings.py`**: Real-time strictness level (`Silent`, `Gentle`, `Cheeky`), per-sensor on/off switches, TTS toggle, and demo mode.

---

## 2. HCI Principles Implemented (Section 11)

| Principle | Implementation in Buddy | Course Talking Point |
| :--- | :--- | :--- |
| **Visibility of system status** (Nielsen) | Face emotion and live timer status strip continuously indicate state (`READY`, `FOCUS`, `BREAK`). | *"You can tell what state it is in at a glance."* |
| **User control and freedom** (Nielsen) | `"take a break now"` always works; strictness level selector; every sensor has an instant off-switch. | *"The Buddy suggests, the user decides."* |
| **Match with real world** | Human facial expressions (blinks, side-eyes) and Pomodoro rhythm. | *"People already read faces, so no manual is needed."* |
| **Minimalist, calm design** | Ambient cue, short spoken lines, non-nagging feedback. | *"An ambient signal, not another notification."* |
| **Non-judgmental feedback** | Interruption timeline shows frequency and timing with zero scores, grades, or blame. | *"It makes the pattern visible without making anyone feel monitored."* |
| **Wizard of Oz prototyping** | Physical sensor hardware is simulated through UI buttons and keyboard triggers. | *"We tested the interaction before building any hardware."* |

---

## 3. Setup and Prerequisites

### System Requirements
- **Python 3.10+** (uses standard library `tkinter`).
- **Operating Systems**: Linux (Ubuntu, Debian, Pop!_OS, Fedora), macOS, Windows.

### Installation Steps

1. **Clone or navigate to the repository**:
   ```bash
   cd /home/pranshu05/GithubRepos/smart_desk_buddy
   ```

2. **Ensure Tkinter is installed**:
   - **Ubuntu / Debian / Pop!_OS**:
     ```bash
     sudo apt update && sudo apt install -y python3-tk
     ```
   - **macOS / Windows**:
     Tkinter comes pre-installed with standard python.org installers.

3. **(Optional) Enable Spoken Voice (Text-to-Speech)**:
   ```bash
   pip install pyttsx3
   ```
   *Note: If `pyttsx3` is not installed or fails, the Buddy runs silently with speech bubbles.*

---

## 4. How to Run

### A. Run Full Integrated Prototype (Phases 3 & 5)
Runs the unified app combining Pransu's animated OLED face with Pranshu's Brain:

```bash
python3 main.py
```

### B. Run Standalone Brain Demo (Phase 1)
Runs Pranshu's Brain independently with the console-logging `FakeFace`:

```bash
# Graphical UI (if Tkinter / X11 display is active):
python3 standalone.py

# Headless Terminal Console / CLI Mode:
python3 standalone.py --cli
```

### C. Run Standalone Face or Summary (Phase 2)
Pransu's modules can also be tried independently:
```bash
python3 ui.py       # Keys: 1-6 change face, Space speaks, S summary, Q quit
python3 summary.py  # Displays sample end-of-session summary
```

### D. Run Automated Test Suite
Verifies all 14 unit and integration tests across rules, lifecycle, timers, and assistant logic:

```bash
python3 test_buddy.py -v
```

---

## 5. Walkthrough of the 2-Minute Demo Script (Section 12)

Use **Demo Mode** (`60s` focus, `15s` break) for presentations:

1. **Hook (15s)**: *"Students get interrupted all the time but rarely see the pattern. Meet the Desk Buddy."*
2. **Wake it (10s)**: Type `"Hi ESP"` in the chat box. The Buddy wakes up with a friendly greeting.
3. **Start focus (10s)**: Type `"start focus"` (or click **Start Focus** in settings/standalone). The face turns calm and focused; the timer starts.
4. **Motion (20s)**:
   - Click **Fidget [F]**: Buddy gives a quiet side-eye (no words).
   - Click **Fidget [F]** again: Buddy says *"Almost there, 25 minutes left."*
   - Click **Leave Seat [L]**: Buddy gives side-eye and says *"Not break time yet, 25 minutes to go. Want a break now?"*
5. **Digital distraction (15s)**: Click **Switch Tab [T]** or **Phone [P]**: Soft side-eye without harsh scolding.
6. **User control (10s)**: Type `"take a break now"`. The Buddy happily agrees: *"Break time. Your call."* Demonstrate the strictness setting in the settings panel.
7. **Summary (20s)**: When session ends, review the non-judgmental timeline and neutral observation sentence.
8. **Close (20s)**: Conclude with testing insights and user feedback.

---

## 6. Project Deliverables

- **`v1_working/`**: Baseline snapshot created at hand-off of Phase 3.
- **`v2_final/`**: Final production release incorporating Phase 4 user testing feedback.
- **`REPORT_DRAFT.md`**: Complete 6-section course project report draft.
