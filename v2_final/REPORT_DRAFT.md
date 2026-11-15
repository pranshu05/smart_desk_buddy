# Smart Desk Buddy — HCI Course Project Report Draft

**Course:** Human-Computer Interaction (HCI)  
**Date:** November 16, 2026  
**Authors:** Pranshu (The Brain: Phases 1, 3, 5) & Pransu (The Face: Phases 2, 4, 6)  
**Artifact / Release:** `v2_final`

---

## 1. The Problem and Who Has It (from our Needfinding)
*Written by Pranshu*

University students engaged in intense cognitive work—such as software development, remote internships, and technical coursework—face a continuous barrage of digital and physical interruptions. In our preliminary needfinding interviews with computing undergraduates, a consistent behavioral paradox emerged: **students get interrupted frequently throughout study blocks, but they rarely see or understand the underlying pattern of their own distractions.**

A typical study session starts with good intentions, but quickly fractures:
- A student opens a quick search, gets diverted into a social feed or tab rabbit hole.
- A phone vibrates across the desk, leading to ten minutes of unintentional doomscrolling.
- Restlessness sets in after fifteen minutes, causing the student to wander away from their desk without a plan.

Existing productivity tools address this problem aggressively:
1. **Hard Site Blockers (e.g., Freedom, Cold Turkey)**: Rely on technological restriction. Students reported that rigid lockouts foster resentment, prompt workarounds (e.g., switching to mobile devices), and fail to cultivate intrinsic self-regulation.
2. **Surveillance & Proctoring Software**: Track keystrokes and webcam movements with punitive scores, making users feel monitored and anxious.
3. **Traditional Pomodoro Timers**: Present sterile numerical countdowns followed by jarring buzzer alarms that shatter cognitive flow.

**Our Core HCI Challenge:** How might we make interruption patterns visible to students without nagging, policing, or inducing guilt, while keeping the user in full control of their focus environment?

---

## 2. Our Design Idea and Why, with the HCI Ideas from Section 11
*Written by Pranshu*

To address this challenge, we designed and built the **Smart Desk Buddy**: an interactive, ambient desktop companion that keeps students company during focus sessions and reacts gently when focus breaks.

Rather than an authoritative monitor, the Buddy acts as an empathetic peer. It sits quietly on screen as an animated retro-style OLED face that mirrors human attention states (calm focus, wandering attention, gentle side-eyes, and cheerful smiles).

```
+-----------------------------------------------------------+
|                   SMART DESK BUDDY                        |
|                                                           |
|       [ PHASE: FOCUS ]                 [ TIMER: 23:45 ]   |
|                                                           |
|                +-------------------------+                |
|                |      (--)     (--)      |  (OLED Canvas) |
|                |          -----          |                |
|                +-------------------------+                |
|       Speech Bubble: "Not break time yet, 15 min to go"   |
|                                                           |
|  +------------------+  +----------------+  +-----------+  |
|  | SIMULATED        |  | ASSISTANT CHAT |  | SETTINGS  |  |
|  | SENSORS (WoZ)    |  |                |  |           |  |
|  | [Fidget] [Leave] |  | "Hi ESP"       |  | Strictness|  |
|  | [Tab]    [Phone] |  | "How am I doing"  | Sensors   |  |
|  +------------------+  +----------------+  +-----------+  |
+-----------------------------------------------------------+
```

### Theoretical Grounding (HCI Choices from Section 11)

Our design directly applies six established HCI principles:

1. **Visibility of System Status (Nielsen)**:
   - *Prototype visible:* The OLED facial expression, the status header (`READY`, `FOCUS`, `BREAK`), and the live countdown strip continuously communicate the active state.
   - *Core insight:* *"You can tell what state it is in at a glance."* No hidden background processing.

2. **User Control and Freedom (Nielsen)**:
   - *Prototype visible:* The user command `"take a break now"` is **always granted** immediately, overriding any active timer. The settings card provides real-time on/off toggle switches for every individual sensor and adjustable strictness levels (`Silent`, `Gentle`, `Cheeky`).
   - *Core insight:* *"The Buddy suggests, the user decides."*

3. **Match with the Real World**:
   - *Prototype visible:* Natural human facial movements (subtle pupil glances, slow resting blinks, surprised brow raises) paired with the familiar rhythm of a Pomodoro work/rest cycle.
   - *Core insight:* *"People already instinctively read faces; no instruction manual is needed."*

4. **Minimalist, Calm Design**:
   - *Prototype visible:* A compact dark-themed card interface (`#0d1117`), concise ambient spoken lines, and no intrusive modal pop-ups, flashing alerts, or buzzer alarms.
   - *Core insight:* *"An ambient signal, not another notification."*

5. **Non-Judgmental Feedback**:
   - *Prototype visible:* The end-of-session summary displays an objective interruption timeline and a neutral observation (e.g., *"Focus dipped most around minute 18 to 22"*). No letter grades, performance percentages, or guilt-inducing metrics.
   - *Core insight:* *"It makes the pattern visible without making anyone feel monitored."*

6. **Wizard of Oz Prototyping**:
   - *Prototype visible:* Physical sensors (PIR motion, tab hooks, phone sensors) are simulated via intuitive UI triggers and keyboard shortcuts `[F, L, R, T, P]`.
   - *Core insight:* *"We tested the interaction dynamics before committing to dedicated hardware."*

---

## 3. How the Prototype Works: Screenshots and Walkthrough
*Section contributed by Pransu*

The prototype integrates the Brain (`engine.py`, `rules.py`, `sensors.py`, `assistant.py`, `settings.py`) with the Face (`ui.py`, `face.py`, `summary.py`, `theme.py`).

### Key Views & Captions
- **Figure 1 — The Focused Companion**: During an active 25-minute session, the Buddy displays half-closed, calm eyes with slower blink intervals, establishing an ambient co-working presence.
- **Figure 2 — The Non-Judgmental Interruption**: When a distraction occurs (e.g., leaving the desk or opening a tab), the Buddy glances sideways with a raised eyebrow and displays a gentle prompt: *"Not break time yet, 15 minutes to go. Want to stretch instead?"*
- **Figure 3 — Natural Assistant Interaction**: The user wakes the Buddy with `"Hi ESP"` and asks `"how am I doing?"`. The assistant parses the session log and returns an encouraging, non-judgmental progress report.
- **Figure 4 — End-of-Session Pattern Timeline**: The summary modal draws a multi-lane timeline plotting interruption dots against session minutes, highlighting clusters without judgment.

---

## 4. How We Tested It and What Testers Said
*Section contributed by Pransu*

We evaluated the `v1_working` prototype with **three computer science classmates** in individual 10-minute testing sessions. Each participant was given a brief overview (*"This is a desk buddy for focus sessions; please think out loud"*) without explaining the buttons in advance.

### Participant Tasks
1. Wake the Buddy by typing `"Hi ESP"`.
2. Start a focus session in Demo Mode.
3. Simulate focus breaks: fidgeting, leaving the desk, and switching tabs.
4. Inquire about focus status by typing `"how am I doing?"`.
5. Trigger an early break with `"take a break now"` and review the end-of-session summary.

### Summary of Tester Responses

| Evaluation Question | Tester 1 (P1 - 3rd Yr CS) | Tester 2 (P2 - 2nd Yr CS) | Tester 3 (P3 - 4th Yr CS) | Average / Consensus |
| :--- | :--- | :--- | :--- | :--- |
| **Helpful or annoying?** *(1 to 5)* | **4 / 5** — *"The side-eye made me smile instead of feeling yelled at."* | **5 / 5** — *"Felt like having a quiet study buddy in the room."* | **4 / 5** — *"Companion tone is nice; needs quiet mode for library."* | **4.33 / 5** |
| **Felt watched or judged?** *(Yes / No)* | **No** — *"It didn't show red warning boxes or give me an 'F' score."* | **No** — *"Neutral timeline felt like a mirror, not a boss."* | **No** — *"It offers a break instead of scolding you."* | **0 / 3 Felt Judged** |
| **Face & mood clarity?** *(1 to 5)* | **5 / 5** — *"Side-eye and sleepy face are immediately obvious."* | **4 / 5** — *"Instant recognition; talking mouth looks cool."* | **5 / 5** — *"OLED aesthetic gives it personality."* | **4.67 / 5** |
| **Would keep on your desk?** *(Yes / Maybe / No)* | **Yes** — *"Would use it during coding sprints."* | **Yes** — *"Especially if I can toggle off certain sensors."* | **Maybe** — *"Would want instant mute toggle for silent library use."* | **2 Yes, 1 Maybe** |

### Top Two Problems Identified by Testers
1. **Problem 1 — Noise Sensitivity in Quiet Environments**: When spoken text-to-speech was enabled, unexpected audio could disrupt quiet study areas (e.g., campus libraries). Testers wanted an absolute `Silent` mode that keeps facial expressions while guaranteeing zero sound and zero speech bubbles.
2. **Problem 2 — Immediate Visual Confirmation for Mode Changes**: When switching between standard mode (25m) and Demo Mode (60s), testers were uncertain whether the timer had adapted until they clicked Start. They requested immediate status strip updates upon toggling settings.

---

## 5. What We Changed Because of the Tests, and What We Would Do Next
*Written by Pranshu*

Following user feedback from Phase 4, we implemented the following concrete adjustments for our `v2_final` deliverable:

### Changes Made for `v2_final`
1. **Immediate Timer Synchronization (`engine.py`)**:
   - Added immediate listener dispatch (`self._notify_timer()`) upon toggling Demo Mode in `engine.set_demo_mode()`. When the user checks "Demo Mode" in the settings card while idle, the top timer display snaps instantly from `25:00` to `01:00`, confirming the setting change before session start.
2. **Dedicated Silent Strictness Mode with Speech Suppression**:
   - Formalized the `Silent` mode in `rules.py` and `engine.py`. In Silent mode, the Buddy communicates strictly through eye and brow movements (glances, smiles, blinks), completely suppressing speech bubbles and audio synthesis.
3. **Integrated Timeline Summaries in Assistant Dialogue**:
   - Linked `summary.summarize(log)` directly to the `"how am I doing?"` chat handler in `assistant.py`. When asked about focus status, the assistant dynamically surfaces the neutral observation sentence alongside counts, reinforcing non-judgmental pattern visibility.

### What We Would Do Next
If we had another iteration cycle, our next steps would include:
1. **Physical Embedded Deployment**: Porting the software prototype to an ESP32 microcontroller with a physical 0.96" I2C monochrome OLED display and miniature servo motors for subtle head tilts.
2. **True Non-Invasive Sensing**: Replacing Wizard of Oz buttons with a low-cost ultrasonic or passive infrared (PIR) desk sensor and a lightweight local operating system hook for tab changes.
3. **Longitudinal Habit Tracking**: Storing anonymized session logs locally across multiple days to reveal weekly focus rhythms (e.g., *"You focus best between 10 AM and 12 PM"*).

---

## 6. Honest Limits: Small Sample and Simulated Sensors
*Written by Pranshu*

To maintain academic rigor and transparency, we acknowledge the following limitations in our evaluation:

1. **Simulated Sensing (Wizard of Oz)**:
   - In this prototype, sensor inputs (fidgeting, leaving the desk, tab switching, phone pickups) are triggered manually via UI buttons and keyboard shortcuts. While this allowed us to study the human-interaction dynamics and conversational tone without sensor noise or calibration failures, it does not capture the latency, false positives, or physical friction of real hardware sensors.
2. **Small Tester Sample Size ($N=3$)**:
   - Our user testing was conducted with three undergraduate computer science students. While their feedback provided valuable qualitative guidance regarding tone and aesthetic clarity, a sample of three cannot establish generalizable conclusions across diverse student demographics, non-technical disciplines, or neurodivergent learners (e.g., students with ADHD).
3. **Short Evaluation Timeframe**:
   - Test sessions lasted approximately 10 minutes per participant using accelerated demo timings. Long-term phenomena—such as companion fatigue, habituation to ambient side-eyes, or potential distraction caused by the face itself over multi-hour study blocks—require longitudinal study over several weeks.

---

## 7. Conclusion

The Smart Desk Buddy demonstrates that productivity software does not need to be punitive or surveillance-driven to encourage healthy work habits. By combining Nielsen's principles of system visibility and user freedom with non-judgmental pattern feedback and an expressive ambient face, the Buddy successfully transforms the Pomodoro timer from an impersonal clock into an encouraging, respectful study companion.
