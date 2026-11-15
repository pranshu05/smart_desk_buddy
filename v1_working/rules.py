"""
rules.py - Smart Desk Buddy Reaction Rules
Defines shared word lists and reaction logic mapping events + strictness level
to Buddy emotions and gentle spoken lines.

HCI Principles:
- Nielsen: User control and freedom ("take a break now" always works)
- Non-judgmental feedback: Gentle companion tone, never scolding or nagging
- Minimalist, calm design: Short, ambient lines
"""

from typing import Optional, Tuple

# Shared Word Lists per Section 4 Contract
EVENTS = [
    "SESSION_START",
    "SEAT_LEAVE",
    "SEAT_RETURN",
    "FIDGET",
    "TAB_SWITCH",
    "PHONE",
    "BREAK_REQUEST",
]

EMOTIONS = [
    "idle",
    "focus",
    "side_eye",
    "talking",
    "happy",
    "sleepy",
]

STRICTNESS_LEVELS = [
    "Silent",
    "Gentle",  # Default
    "Cheeky",
]


def get_reaction(
    event: str,
    strictness: str = "Gentle",
    state: str = "focus",
    fidget_count: int = 1,
    remaining_minutes: int = 25,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Decides the reaction (emotion, spoken_text) based on event, strictness,
    current state ('idle', 'focus', 'break'), fidget count, and time left.

    Returns:
        (emotion, spoken_text)
        - emotion: one of EMOTIONS or None if no face change
        - spoken_text: text to speak/display in speech bubble, or None for silent
    """
    # Guard against invalid events or strictness
    if event not in EVENTS:
        return (None, None)

    # 1. "Take a break now" must always work in any state or strictness
    if event == "BREAK_REQUEST":
        if strictness == "Silent":
            return ("happy", None)
        elif strictness == "Cheeky":
            return ("happy", "You win this round! Break time granted.")
        else:  # Gentle (default)
            return ("happy", "Break time. Your call.")

    # 2. Rule from PDF: During a break the Buddy never reacts to movement
    if state == "break":
        if event in ("FIDGET", "SEAT_LEAVE", "TAB_SWITCH", "PHONE"):
            # Buddy relaxes; no reaction to movement during break
            return (None, None)
        elif event == "SEAT_RETURN":
            if strictness == "Silent":
                return ("happy", None)
            elif strictness == "Cheeky":
                return ("happy", "Back to the lounge! Enjoy the rest of your break.")
            else:
                return ("happy", "Welcome back. Still break time!")
        elif event == "SESSION_START":
            # Handled below
            pass

    # 3. Session Start
    if event == "SESSION_START":
        if strictness == "Silent":
            return ("focus", None)
        elif strictness == "Cheeky":
            return ("focus", "Focus time! Lock in, let's see how long you last!")
        else:  # Gentle
            return ("focus", "Let's focus together! Starting your session now.")

    # 4. Reaction Table during focus session
    # In Silent mode: Buddy only changes its face, never speaks
    if strictness == "Silent":
        if event in ("FIDGET", "SEAT_LEAVE", "TAB_SWITCH", "PHONE"):
            return ("side_eye", None)
        elif event == "SEAT_RETURN":
            return ("happy", None)
        return (None, None)

    # In Cheeky mode: playful lines for the same events
    if strictness == "Cheeky":
        rem = max(1, remaining_minutes)
        if event == "FIDGET":
            if fidget_count == 1:
                return ("side_eye", f"Wiggle wiggle! Still {rem} minutes to go though.")
            elif fidget_count == 2:
                return ("side_eye", f"Chair on fire? {rem} minutes left!")
            else:
                return ("side_eye", "Okay dancing queen, time for an early break?")
        elif event == "SEAT_LEAVE":
            return ("side_eye", f"Abandoning ship with {rem} minutes left? I see you!")
        elif event == "SEAT_RETURN":
            return ("happy", "Look who decided to show up! Welcome back.")
        elif event == "TAB_SWITCH":
            return ("side_eye", "Caught you tab surfing! Back to work.")
        elif event == "PHONE":
            return ("side_eye", f"Doomscrolling alert! Put the glowing rectangle down, {rem} more minutes.")

    # In Gentle mode (default): gentle companion, never nagging
    rem = max(1, remaining_minutes)
    if event == "FIDGET":
        if fidget_count == 1:
            # 1st time: a quiet side-eye, no words
            return ("side_eye", None)
        elif fidget_count == 2:
            # 2nd time: "Almost there, N minutes left."
            return ("side_eye", f"Almost there, {rem} minutes left.")
        else:
            # 3rd time: offers an early break
            return ("side_eye", f"You seem a bit restless with {rem} minutes left. Want to take an early break?")
    elif event == "SEAT_LEAVE":
        # Side-eye and "Not break time yet, N minutes to go. Want a break now?"
        return ("side_eye", f"Not break time yet, {rem} minutes to go. Want a break now?")
    elif event == "SEAT_RETURN":
        # Happy face and "Welcome back."
        return ("happy", "Welcome back.")
    elif event == "TAB_SWITCH":
        # A quiet side-eye, no words
        return ("side_eye", None)
    elif event == "PHONE":
        # Side-eye and "The phone can wait. Just N more minutes."
        return ("side_eye", f"The phone can wait. Just {rem} more minutes.")

    return (None, None)
