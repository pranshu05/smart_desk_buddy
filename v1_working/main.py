"""
main.py - Smart Desk Buddy Phase 3 Connect Entry Point
Connects Pranshu's Brain (engine, sensors, assistant, settings, rules)
with Pransu's Face (ui.py, face.py, summary.py) through the Section 4 Contract.

Zero changes to Brain logic are required to swap between standalone and integrated.
"""

import sys

import assistant
from engine import Engine
import sensors
import settings

# Import Pransu's modules per Section 4 Contract
try:
    import face
    import summary
    import theme
    import ui
except ImportError as e:
    print("=" * 65)
    print(f"Notice: Could not import Pransu's modules ({e}).")
    print("If you are running Phase 1 standalone, run:")
    print("    python3 standalone.py")
    print("Once Pransu provides ui.py, face.py, and summary.py, place them")
    print("in this directory and re-run python3 main.py.")
    print("=" * 65)
    sys.exit(1)


def parse_window_contract(build_result):
    """
    Normalizes the return value of ui.build_window().
    Section 4 contract specifies:
      'build_window() returns the window, the face, and three empty frames
       called sensors, chat and settings'

    Handles both dict representation and 5-tuple representation:
      - (window, face, {'sensors': s, 'chat': c, 'settings': st})
      - (window, face, s, c, st)
    """
    if len(build_result) == 3:
        window, face_obj, frames = build_result
        if isinstance(frames, dict):
            return window, face_obj, frames["sensors"], frames["chat"], frames["settings"]
        elif hasattr(frames, "sensors"):
            return window, face_obj, frames.sensors, frames.chat, frames.settings
        else:
            raise ValueError("Expected frames dict with keys 'sensors', 'chat', 'settings'")
    elif len(build_result) == 5:
        window, face_obj, s_frame, c_frame, set_frame = build_result
        return window, face_obj, s_frame, c_frame, set_frame
    else:
        raise ValueError(
            f"Unexpected return signature from build_window(): got {len(build_result)} items"
        )


def main():
    print("Starting Smart Desk Buddy (Integrated Mode - Phase 3)...")

    # Step 1: Call Pransu's build_window()
    build_result = ui.build_window()
    window, face_instance, sensors_frame, chat_frame, settings_frame = parse_window_contract(build_result)

    # Step 2: Define summary callback adapting to Pransu's summary.py
    def on_show_summary(log):
        if hasattr(summary, "show_summary"):
            unit = "sec" if getattr(engine, "demo_mode", False) else "min"
            length = 60 if getattr(engine, "demo_mode", False) else 25
            summary.show_summary(log, session_length=length, unit=unit, parent=window)

    # Step 3: Instantiate Engine with real face and summary callback
    engine = Engine(
        face=face_instance,
        summary_callback=on_show_summary,
        tk_root=window,
    )

    # Step 4: Bind face status strip to engine's live countdown and state
    if hasattr(face_instance, "bind_engine"):
        face_instance.bind_engine(engine)

    # Step 5: Wire TTS settings toggle to face.set_voice
    if hasattr(face_instance, "set_voice"):
        orig_set_tts = engine.set_tts_enabled
        def hooked_set_tts(on):
            orig_set_tts(on)
            face_instance.set_voice(on)
        engine.set_tts_enabled = hooked_set_tts

    # Step 6: Populate the three contract frames with our Brain panels
    sensors.setup_sensors(sensors_frame, engine, root=window)
    assistant.setup_chat(chat_frame, engine)
    settings.setup_settings(settings_frame, engine)

    print("Smart Desk Buddy connected successfully. Running mainloop...")
    window.mainloop()


if __name__ == "__main__":
    main()
