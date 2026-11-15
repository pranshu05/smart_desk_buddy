# Smart Desk Buddy — Hand-off Context & Agent Prompt for Pransu (The Face)

**Project Location:** `/home/pranshu05/GithubRepos/smart_desk_buddy`  
**Your Partner:** Pranshu (Built The Brain: `engine.py`, `rules.py`, `sensors.py`, `assistant.py`, `settings.py`)  
**Your Role:** Pransu (Building The Face: `ui.py`, `face.py`, `summary.py` — Phases 2, 4, 6)

---

## 1. Summary of What Has Been Done Already

Pranshu has finished **The Brain** (Phases 1, 3, and 5) and verified all automated tests:

1. **`engine.py`**:
   - Manages session lifecycle (`idle` → `focus` → `break` → `idle`).
   - Timers: 25-minute focus session (with 5-minute break), plus Demo Mode (60s focus, 15s break).
   - Event log: Maintains a list of `(minute, event_name)` pairs across the session.
   - Dispatches reactions by calling `face.set_emotion(name)` and `face.say(text)`.
   - Wires `summary.show_summary(log)` upon session completion.

2. **`rules.py`**:
   - Full reaction table mapped by event, strictness (`Silent`, `Gentle`, `Cheeky`), and state.
   - Tone is a gentle companion, never nagging.
   - `"take a break now"` (`BREAK_REQUEST`) is always honored.

3. **`sensors.py`**, **`assistant.py`**, and **`settings.py`**:
   - `sensors.setup_sensors(sensors_frame, engine, root)`: Fills the `sensors` frame with simulation buttons and keyboard shortcuts `[F, L, R, T, P]`.
   - `assistant.setup_chat(chat_frame, engine)`: Fills the `chat` frame with the chat box (woken by `"Hi ESP"`, answers `"how am I doing?"`, etc.).
   - `settings.setup_settings(settings_frame, engine)`: Fills the `settings` frame with strictness radio buttons, sensor on/off toggles, and demo mode.

4. **`main.py`**:
   - Thin integration entry point for Phase 3. It imports `ui.py`, `face.py`, and `summary.py`, calls `build_window()`, creates `Engine`, populates the three frames, and runs the Tkinter mainloop.
   - **Zero changes** to Brain files are needed when you update your files.

---

## 2. The Shared Contract You Must Satisfy (Section 4 of Guide)

Your code only needs to provide three files:

### A. `ui.py`
Must provide a function:
```python
def build_window():
    """
    Returns: (window, face, frames)
    where:
      - window: The main Tk root / window
      - face: The Face instance (from face.py)
      - frames: A dict {'sensors': frame1, 'chat': frame2, 'settings': frame3}
                (or a 5-tuple: window, face, sensors_frame, chat_frame, settings_frame)
    """
```
- **Layout:**
  - Top area: Face display (Canvas simulating an OLED screen).
  - Under face: Speech bubble label / text area.
  - Timer label showing remaining time and state.
  - Bottom area: Three empty frames (`sensors`, `chat`, `settings`) where Pranshu's panels are injected.

### B. `face.py`
Must provide a `Face` class with two methods:
1. `face.set_emotion(name)`:
   - Updates mood to one of the 6 shared emotions:
     - `'idle'` (open eyes, slow blink)
     - `'focus'` (eyes half-closed and calm, no blinking for longer)
     - `'side_eye'` (pupils shifted to one side, one brow slightly raised)
     - `'talking'` (mouth opens and closes while text is shown)
     - `'happy'` (eyes curved like a smile)
     - `'sleepy'` (low eyelids, very slow blink)
2. `face.say(text)`:
   - Displays `text` in the speech bubble under the face.
   - Switches face to `'talking'` while shown.
   - After ~3 seconds, reverts the face back to the previous emotion.
3. Standalone testing feature:
   - Bind keyboard keys `1` to `6` to force each of the 6 emotions directly on screen for testing.

### C. `summary.py`
Must provide a function:
```python
def show_summary(log):
    """
    Args:
        log: list of (minute, event_name) tuples,
             e.g. [(3, 'FIDGET'), (7, 'TAB_SWITCH'), (8, 'TAB_SWITCH'), (14, 'SEAT_LEAVE')]
    """
```
- Draws the end-of-session summary window.
- Visual timeline with one mark per interruption across the session.
- Interruption counts for each kind (`FIDGET`, `SEAT_LEAVE`, `TAB_SWITCH`, `PHONE`).
- One neutral sentence (e.g. *"Focus dipped most around minute 18 to 22."*).
- **HCI Principle:** Non-judgmental feedback — NO scores, NO grades, and NO blame.

---

## 3. Ready-to-Copy Prompt for Pransu's Agent

Copy and paste the prompt in the block below into your AI agent:

```markdown
I am building my half of a 2-person HCI course project called "Smart Desk Buddy" in Python 3 with Tkinter.
My partner Pranshu has already built The Brain (engine.py, sensors.py, rules.py, assistant.py, settings.py) and main.py in `/home/pranshu05/GithubRepos/smart_desk_buddy`.

My role is The Face (Phases 2, 4, and 6). I need to implement:
1. ui.py
2. face.py
3. summary.py

My code must connect with Pranshu's Brain strictly through the Section 4 Contract:

1. ui.py:
   - build_window() creates the main Tkinter window with dark theme aesthetic (dark background, one accent color, clean font).
   - Layout:
     - Top: Face canvas area.
     - Below face: A speech bubble label.
     - Timer label.
     - Bottom: Three empty Tkinter frames named 'sensors', 'chat', and 'settings'.
   - Returns: (window, face, {'sensors': sensors_frame, 'chat': chat_frame, 'settings': settings_frame})

2. face.py:
   - A Face class driving a Tkinter Canvas that imitates a small retro OLED screen (e.g., 128x64 or 256x128 grid drawn with simple rectangles).
   - Eye and mouth animations redraw ~30 times a second using Tkinter's after() for smooth natural blinking.
   - face.set_emotion(name):
     Supports the 6 contract emotions:
     - 'idle': open eyes, slow gentle blink
     - 'focus': calm half-closed eyes, longer interval between blinks
     - 'side_eye': pupils shifted sideways, one brow raised
     - 'talking': animated mouth opening and closing
     - 'happy': curved smile eyes and smile mouth
     - 'sleepy': heavy droopy eyelids, very slow blink
   - face.say(text):
     Updates the speech bubble label with text, moves the mouth in talking animation, and after ~3 seconds reverts to the previous emotion.
   - For standalone testing: bind keyboard keys '1' through '6' to immediately force each emotion on screen.

3. summary.py:
   - show_summary(log):
     log is a list of (minute, event_name) pairs, e.g. [(3, 'FIDGET'), (7, 'TAB_SWITCH'), (8, 'TAB_SWITCH'), (14, 'SEAT_LEAVE')].
     Opens an end-of-session screen with:
     - A graphical timeline showing interruption markers across the session duration (minutes 0 to 25).
     - Breakdown count for each interruption type (FIDGET, SEAT_LEAVE, TAB_SWITCH, PHONE).
     - One neutral, non-judgmental observation sentence (e.g. "Focus dipped most around minute 18 to 22.").
     - HCI Rule: Non-judgmental feedback — strictly no scores, grades, or scolding.
   - Include standalone test harness: when running `python3 summary.py`, open the summary screen using the sample log `[(3, 'FIDGET'), (7, 'TAB_SWITCH'), (8, 'TAB_SWITCH'), (14, 'SEAT_LEAVE')]`.

Requirements:
- Python 3 with built-in Tkinter only.
- Clean, modular, well-commented code.
- Must work standalone (`python3 face.py`, `python3 summary.py`) and seamlessly plug into `python3 main.py` with zero changes to Pranshu's files.
```
