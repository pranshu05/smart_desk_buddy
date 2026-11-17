"""
assistant.py - Smart Desk Buddy Chat Assistant
Fills the 'chat' frame with an interactive chat interface that communicates
with the user and engine.

HCI Principles:
- User control and freedom: "take a break now" is always obeyed
- Non-judgmental feedback: answers "how am I doing?" objectively without scores or blame
- Minimalist, calm companion tone
"""

from typing import Any, List, Tuple

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter.scrolledtext import ScrolledText
except ImportError:
    tk = None
    ttk = None
    ScrolledText = None

try:
    import theme
    HAS_THEME = True
except ImportError:
    HAS_THEME = False


class AssistantBrain:
    """
    Handles natural language commands and dialogue for the Desk Buddy.
    Interprets user queries and coordinates with the Engine and Face.
    """

    def __init__(self, engine: Any):
        self.engine = engine
        self.is_awake = False
        self.volume = 70  # default volume percentage (0-100)

    def process_message(self, text: str) -> str:
        """
        Processes incoming text and returns the response string.
        Also triggers corresponding engine state changes or face reactions.
        """
        clean = text.strip()
        lower = clean.lower()

        # 1. Wake word: "Hi ESP" (tolerant of punctuation and greetings)
        if "hi esp" in lower or "hello esp" in lower or "hey esp" in lower or "esp" in lower:
            self.is_awake = True
            self.engine.face.set_emotion("happy")
            response = "Hi there! I'm awake and ready to keep you company. How can I help?"
            self.engine.face.say(response)
            return response

        # If asleep, remind user how to wake
        if not self.is_awake:
            return "Zzz... (Type 'Hi ESP' to wake me up!)"

        # 2. "start focus"
        if "start focus" in lower or lower == "focus" or "start session" in lower or "start" == lower:
            self.engine.start_focus()
            response = "Starting your focus session now. Calm and locked in!"
            return response

        # 3. "take a break" or "take a break now" (Must always work per Section 4 & 5)
        if "take a break" in lower or "break" in lower or "pause" in lower or "rest" in lower:
            self.engine.take_break()
            response = "Break time. Your call."
            return response

        # 4. "how am I doing?"
        if "how am i doing" in lower or "how's my focus" in lower or "status" in lower or "progress" in lower or "stats" in lower:
            response = self._summarize_performance()
            # Speak concise summary on face
            if hasattr(self.engine, "face") and hasattr(self.engine.face, "say"):
                spoken_line = response.split("\n")[0]
                self.engine.face.say(spoken_line)
            return response

        # 5. Volume controls
        if "volume up" in lower or "louder" in lower:
            self.volume = min(100, self.volume + 15)
            if hasattr(self.engine.face, "set_volume"):
                self.engine.face.set_volume(self.volume)
            response = f"Volume increased to {self.volume}%."
            self.engine.face.say(f"Volume set to {self.volume} percent.")
            return response
        if "volume down" in lower or "quieter" in lower or "softer" in lower:
            self.volume = max(10, self.volume - 15)
            if hasattr(self.engine.face, "set_volume"):
                self.engine.face.set_volume(self.volume)
            response = f"Volume decreased to {self.volume}%."
            self.engine.face.say(f"Volume set to {self.volume} percent.")
            return response

        # 6. Weather
        if "weather" in lower or "forecast" in lower:
            response = "Desk forecast: 22°C and clear indoors. Perfect climate for focused work! ☀️"
            self.engine.face.say("Desk forecast: 22 degrees and clear indoors. Perfect climate for focused work!")
            return response

        # 7. Music
        if "music" in lower or "song" in lower or "playlist" in lower:
            response = "Now spinning: Lo-Fi Chill Study Beats & Ambient Rain 🎧"
            self.engine.face.say("Now spinning: Lo-Fi Chill Study Beats and Ambient Rain.")
            return response

        # 8. Summary / End Session
        if "summary" in lower or "end session" in lower or "finish" in lower:
            self.engine.face.say("Opening your session summary.")
            self.engine.end_session_and_show_summary()
            return "Session ended! Opening your summary timeline now."

        # Fallback gentle guide
        fallback_msg = (
            "I can help with:\n"
            "• 'start focus' - begin a focus timer\n"
            "• 'take a break now' - pause for a short rest\n"
            "• 'how am I doing?' - check current session status\n"
            "• 'weather', 'music', 'volume up/down', or 'summary'"
        )
        self.engine.face.say("I can help with focus, breaks, status, weather, or music.")
        return fallback_msg

    def _summarize_performance(self) -> str:
        """
        Generates a non-judgmental summary of current session progress
        from the engine's event log.
        """
        if self.engine.state == "idle":
            return "No active focus session right now. Type 'start focus' to start one!"

        if self.engine.state == "break":
            return "You're currently taking a break. Rest your eyes and recharge!"

        log = self.engine.get_event_log()
        rem_min = self.engine._get_remaining_minutes()
        elapsed_min = self.engine._get_current_minute()

        fidgets = sum(1 for m, ev in log if ev == "FIDGET")
        seat_leaves = sum(1 for m, ev in log if ev == "SEAT_LEAVE")
        tabs = sum(1 for m, ev in log if ev == "TAB_SWITCH")
        phones = sum(1 for m, ev in log if ev == "PHONE")
        total_interruptions = fidgets + seat_leaves + tabs + phones

        try:
            import summary
            if hasattr(summary, "summarize"):
                s_data = summary.summarize(log, session_length=25 if not self.engine.demo_mode else 60, unit="min" if not self.engine.demo_mode else "sec")
                neutral_sentence = s_data.get("sentence", "")
            else:
                neutral_sentence = ""
        except Exception:
            neutral_sentence = ""

        if total_interruptions == 0:
            msg = (
                f"You've been focusing for about {elapsed_min} minute(s) with 0 interruptions! "
                f"You're in the zone. {rem_min} minute(s) remaining."
            )
            if neutral_sentence:
                msg += f"\nPattern: {neutral_sentence}"
            return msg
        else:
            breakdown = []
            if fidgets:
                breakdown.append(f"{fidgets} fidget{'s' if fidgets > 1 else ''}")
            if seat_leaves:
                breakdown.append(f"{seat_leaves} seat departure{'s' if seat_leaves > 1 else ''}")
            if tabs:
                breakdown.append(f"{tabs} tab switch{'es' if tabs > 1 else ''}")
            if phones:
                breakdown.append(f"{phones} phone check{'s' if phones > 1 else ''}")

            items_str = ", ".join(breakdown)
            msg = (
                f"You're at minute {elapsed_min} with {rem_min} minutes to go. "
                f"Recorded moments so far: {items_str}. "
                f"Focus is a rhythm — you're doing well, keep it up!"
            )
            if neutral_sentence:
                msg += f"\nObservation: {neutral_sentence}"
            return msg


def setup_chat(parent_frame, engine):
    """
    Fills the provided parent_frame with the chat box UI.

    Args:
        parent_frame: Tkinter Frame where chat UI is built.
        engine: Engine instance.
    Returns:
        assistant_brain: AssistantBrain instance.
    """
    if tk is None:
        return AssistantBrain(engine)

    assistant = AssistantBrain(engine)

    bg_color = theme.PANEL if HAS_THEME else (parent_frame.cget("bg") if hasattr(parent_frame, "cget") else "#2d2d2d")
    fg_title = theme.ACCENT if HAS_THEME else "#e0e0e0"
    fg_muted = theme.MUTED if HAS_THEME else "#aaaaaa"
    title_font = theme.font(10, "bold", mono=True, root=parent_frame) if HAS_THEME else ("Helvetica", 11, "bold")
    sub_font = theme.font(9, root=parent_frame) if HAS_THEME else ("Helvetica", 9)

    # Header
    header = tk.Label(
        parent_frame,
        text="ASSISTANT CHAT",
        font=title_font,
        fg=fg_title,
        bg=bg_color,
        pady=2,
    )
    header.pack(anchor="w", padx=6, pady=(2, 1))

    subtitle = tk.Label(
        parent_frame,
        text="Type 'Hi ESP' to wake, or ask 'how am I doing?':",
        font=sub_font,
        fg=fg_muted,
        bg=bg_color,
    )
    subtitle.pack(anchor="w", padx=6, pady=(0, 4))

    # Chat history display
    chat_bg = "#0d1117" if HAS_THEME else "#1e1e1e"
    chat_fg = theme.TEXT if HAS_THEME else "#e0e0e0"
    chat_display = ScrolledText(
        parent_frame,
        wrap="word",
        height=8,
        font=sub_font,
        bg=chat_bg,
        fg=chat_fg,
        insertbackground=chat_fg,
        relief="flat",
        bd=1,
    ) if ScrolledText else tk.Text(parent_frame, wrap="word", height=8, font=sub_font, bg=chat_bg, fg=chat_fg)
    chat_display.pack(fill="both", expand=True, padx=4, pady=2)
    chat_display.tag_config("user", foreground=theme.ACCENT if HAS_THEME else "#80d8ff", font=theme.font(9, "bold", root=parent_frame) if HAS_THEME else ("Helvetica", 9, "bold"))
    chat_display.tag_config("buddy", foreground="#5eead4" if HAS_THEME else "#b9f6ca")
    chat_display.tag_config("system", foreground=theme.MUTED if HAS_THEME else "#ffd54f", font=theme.font(8, "italic", root=parent_frame) if HAS_THEME else ("Helvetica", 8, "italic"))

    # Initial welcome tip in display
    chat_display.insert("end", "System: Type 'Hi ESP' to wake the buddy.\n", "system")
    chat_display.config(state="disabled")

    # Input controls container
    input_box = tk.Frame(parent_frame, bg=bg_color)
    input_box.pack(fill="x", padx=4, pady=(4, 4))

    entry = tk.Entry(
        input_box,
        font=theme.font(10, root=parent_frame) if HAS_THEME else ("Helvetica", 10),
        bg=theme.BUTTON if HAS_THEME else "#3c3f41",
        fg=theme.TEXT if HAS_THEME else "#ffffff",
        insertbackground=theme.TEXT if HAS_THEME else "#ffffff",
        relief="flat",
        bd=1,
    )
    entry.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=3)

    def on_send(event=None):
        msg = entry.get().strip()
        if not msg:
            return
        entry.delete(0, "end")

        # Append user message
        chat_display.config(state="normal")
        chat_display.insert("end", f"You: {msg}\n", "user")

        # Process and append response
        reply = assistant.process_message(msg)
        chat_display.insert("end", f"Buddy: {reply}\n\n", "buddy")
        chat_display.see("end")
        chat_display.config(state="disabled")

    send_btn = tk.Button(
        input_box,
        text="Send",
        command=on_send,
        font=theme.font(9, "bold", root=parent_frame) if HAS_THEME else ("Helvetica", 9, "bold"),
        fg="#04222b" if HAS_THEME else "#ffffff",
        bg=theme.ACCENT if HAS_THEME else "#00897b",
        activebackground="#a6f0ff" if HAS_THEME else "#26a69a",
        activeforeground="#04222b" if HAS_THEME else "#ffffff",
        relief="flat",
        bd=1,
        padx=12,
        cursor="hand2",
    )
    send_btn.pack(side="right")

    entry.bind("<Return>", on_send)

    return assistant
