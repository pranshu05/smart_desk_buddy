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

        # 1. Wake word: "Hi ESP"
        if "hi esp" in lower or "hello esp" in lower or "hey esp" in lower:
            self.is_awake = True
            self.engine.face.set_emotion("happy")
            response = "Hi there! I'm awake and ready to keep you company. How can I help?"
            self.engine.face.say(response)
            return response

        # If asleep, remind user how to wake
        if not self.is_awake:
            return "Zzz... (Type 'Hi ESP' to wake me up!)"

        # 2. "start focus"
        if "start focus" in lower or lower == "focus" or "start session" in lower:
            self.engine.start_focus()
            response = "Starting your focus session now. Calm and locked in!"
            return response

        # 3. "take a break" or "take a break now" (Must always work per Section 4 & 5)
        if "take a break" in lower or "take a break now" in lower or "break now" in lower or lower == "break":
            self.engine.take_break()
            response = "Break time. Your call."
            return response

        # 4. "how am I doing?"
        if "how am i doing" in lower or "how's my focus" in lower or "status" in lower:
            return self._summarize_performance()

        # 5. Volume controls
        if "volume up" in lower or "louder" in lower:
            self.volume = min(100, self.volume + 15)
            return f"Volume increased to {self.volume}%."
        if "volume down" in lower or "quieter" in lower or "softer" in lower:
            self.volume = max(10, self.volume - 15)
            return f"Volume decreased to {self.volume}%."

        # 6. Weather
        if "weather" in lower or "forecast" in lower:
            return "Desk forecast: 22°C and clear indoors. Perfect climate for focused work! ☀️"

        # 7. Music
        if "music" in lower or "song" in lower or "playlist" in lower:
            return "Now spinning: Lo-Fi Chill Study Beats & Ambient Rain 🎧"

        # Fallback gentle guide
        return (
            "I can help with:\n"
            "• 'start focus' - begin a focus timer\n"
            "• 'take a break now' - pause for a short rest\n"
            "• 'how am I doing?' - check current session status\n"
            "• 'weather', 'music', or 'volume up/down'"
        )

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

        if total_interruptions == 0:
            return (
                f"You've been focusing for about {elapsed_min} minute(s) with 0 interruptions! "
                f"You're in the zone. {rem_min} minute(s) remaining."
            )
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
            return (
                f"You're at minute {elapsed_min} with {rem_min} minutes to go. "
                f"Recorded moments so far: {items_str}. "
                f"Focus is a rhythm — you're doing well, keep it up!"
            )


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

    bg_color = parent_frame.cget("bg") if hasattr(parent_frame, "cget") else "#2d2d2d"

    # Header
    header = tk.Label(
        parent_frame,
        text="Buddy Assistant Chat",
        font=("Helvetica", 11, "bold"),
        fg="#e0e0e0",
        bg=bg_color,
        pady=4,
    )
    header.pack(anchor="w", padx=8, pady=(4, 2))

    subtitle = tk.Label(
        parent_frame,
        text="Type 'Hi ESP' to wake your buddy, or ask questions below:",
        font=("Helvetica", 9),
        fg="#aaaaaa",
        bg=bg_color,
    )
    subtitle.pack(anchor="w", padx=8, pady=(0, 4))

    # Chat history display
    chat_display = ScrolledText(
        parent_frame,
        wrap="word",
        height=8,
        font=("Helvetica", 9),
        bg="#1e1e1e",
        fg="#e0e0e0",
        insertbackground="#ffffff",
        relief="flat",
        bd=2,
    ) if ScrolledText else tk.Text(parent_frame, wrap="word", height=8, font=("Helvetica", 9), bg="#1e1e1e", fg="#e0e0e0")
    chat_display.pack(fill="both", expand=True, padx=8, pady=4)
    chat_display.tag_config("user", foreground="#80d8ff", font=("Helvetica", 9, "bold"))
    chat_display.tag_config("buddy", foreground="#b9f6ca")
    chat_display.tag_config("system", foreground="#ffd54f", font=("Helvetica", 8, "italic"))

    # Initial welcome tip in display
    chat_display.insert("end", "System: Type 'Hi ESP' to wake the buddy.\n", "system")
    chat_display.config(state="disabled")

    # Input controls container
    input_box = tk.Frame(parent_frame, bg=bg_color)
    input_box.pack(fill="x", padx=8, pady=(2, 6))

    entry = tk.Entry(
        input_box,
        font=("Helvetica", 10),
        bg="#3c3f41",
        fg="#ffffff",
        insertbackground="#ffffff",
        relief="groove",
        bd=1,
    )
    entry.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=4)

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
        font=("Helvetica", 9, "bold"),
        fg="#ffffff",
        bg="#00897b",
        activebackground="#26a69a",
        activeforeground="#ffffff",
        relief="raised",
        bd=1,
        padx=12,
        cursor="hand2",
    )
    send_btn.pack(side="right")

    entry.bind("<Return>", on_send)

    return assistant
