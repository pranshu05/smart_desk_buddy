"""
test_buddy.py - Comprehensive Unit & Integration Test Suite
Verifies Brain components: rules, engine, sensors, assistant, settings,
and contract compliance.
"""

import unittest
from typing import List, Tuple

import assistant
from engine import Engine
import rules


class MockFace:
    """Mock Face recording calls to set_emotion and say."""
    def __init__(self):
        self.emotions: List[str] = []
        self.speeches: List[str] = []
        self.current_emotion = "idle"
        self.last_speech = ""

    def set_emotion(self, name: str) -> None:
        self.emotions.append(name)
        self.current_emotion = name

    def say(self, text: str) -> None:
        self.speeches.append(text)
        self.last_speech = text


class TestRules(unittest.TestCase):
    """Verifies all reaction rules and word lists in rules.py."""

    def test_word_lists(self):
        self.assertEqual(len(rules.EVENTS), 7)
        self.assertIn("SESSION_START", rules.EVENTS)
        self.assertIn("SEAT_LEAVE", rules.EVENTS)
        self.assertIn("SEAT_RETURN", rules.EVENTS)
        self.assertIn("FIDGET", rules.EVENTS)
        self.assertIn("TAB_SWITCH", rules.EVENTS)
        self.assertIn("PHONE", rules.EVENTS)
        self.assertIn("BREAK_REQUEST", rules.EVENTS)

        self.assertEqual(len(rules.EMOTIONS), 6)
        self.assertIn("idle", rules.EMOTIONS)
        self.assertIn("focus", rules.EMOTIONS)
        self.assertIn("side_eye", rules.EMOTIONS)
        self.assertIn("talking", rules.EMOTIONS)
        self.assertIn("happy", rules.EMOTIONS)
        self.assertIn("sleepy", rules.EMOTIONS)

        self.assertEqual(rules.STRICTNESS_LEVELS, ["Silent", "Gentle", "Cheeky"])

    def test_break_request_always_works(self):
        # In Gentle
        emo, text = rules.get_reaction("BREAK_REQUEST", strictness="Gentle")
        self.assertEqual(emo, "happy")
        self.assertIn("Break time", text)

        # In Cheeky
        emo, text = rules.get_reaction("BREAK_REQUEST", strictness="Cheeky")
        self.assertEqual(emo, "happy")
        self.assertIn("Break time", text)

        # In Silent
        emo, text = rules.get_reaction("BREAK_REQUEST", strictness="Silent")
        self.assertEqual(emo, "happy")
        self.assertIsNone(text)

    def test_gentle_mode_distractions(self):
        # 1st FIDGET: quiet side-eye, no words
        emo, text = rules.get_reaction("FIDGET", strictness="Gentle", fidget_count=1, remaining_minutes=15)
        self.assertEqual(emo, "side_eye")
        self.assertIsNone(text)

        # 2nd FIDGET: side-eye, "Almost there, N minutes left."
        emo, text = rules.get_reaction("FIDGET", strictness="Gentle", fidget_count=2, remaining_minutes=15)
        self.assertEqual(emo, "side_eye")
        self.assertIn("Almost there, 15 minutes left.", text)

        # 3rd FIDGET: offers an early break
        emo, text = rules.get_reaction("FIDGET", strictness="Gentle", fidget_count=3, remaining_minutes=10)
        self.assertEqual(emo, "side_eye")
        self.assertIn("restless", text.lower())

        # SEAT_LEAVE: side-eye and "Not break time yet, N minutes to go."
        emo, text = rules.get_reaction("SEAT_LEAVE", strictness="Gentle", remaining_minutes=15)
        self.assertEqual(emo, "side_eye")
        self.assertIn("Not break time yet, 15 minutes to go.", text)

        # SEAT_RETURN: happy face and "Welcome back."
        emo, text = rules.get_reaction("SEAT_RETURN", strictness="Gentle")
        self.assertEqual(emo, "happy")
        self.assertEqual(text, "Welcome back.")

        # TAB_SWITCH: quiet side-eye, no words
        emo, text = rules.get_reaction("TAB_SWITCH", strictness="Gentle")
        self.assertEqual(emo, "side_eye")
        self.assertIsNone(text)

        # PHONE: side-eye and "The phone can wait. Just N more minutes."
        emo, text = rules.get_reaction("PHONE", strictness="Gentle", remaining_minutes=8)
        self.assertEqual(emo, "side_eye")
        self.assertIn("The phone can wait. Just 8 more minutes.", text)

    def test_silent_mode(self):
        for ev in ("FIDGET", "SEAT_LEAVE", "TAB_SWITCH", "PHONE"):
            emo, text = rules.get_reaction(ev, strictness="Silent")
            self.assertEqual(emo, "side_eye")
            self.assertIsNone(text)

        emo, text = rules.get_reaction("SEAT_RETURN", strictness="Silent")
        self.assertEqual(emo, "happy")
        self.assertIsNone(text)

    def test_break_movement_ignored(self):
        # Rule from PDF: During a break the Buddy never reacts to movement
        for ev in ("FIDGET", "SEAT_LEAVE", "TAB_SWITCH", "PHONE"):
            emo, text = rules.get_reaction(ev, strictness="Gentle", state="break")
            self.assertIsNone(emo)
            self.assertIsNone(text)


class TestEngine(unittest.TestCase):
    """Verifies Engine lifecycle, event routing, filtering, and timers."""

    def setUp(self):
        self.mock_face = MockFace()
        self.summary_logs = []
        def summary_cb(log):
            self.summary_logs.append(log)
        self.engine = Engine(face=self.mock_face, summary_callback=summary_cb)

    def test_session_start_lifecycle(self):
        self.assertEqual(self.engine.state, "idle")
        self.engine.start_focus()
        self.assertEqual(self.engine.state, "focus")
        self.assertEqual(self.mock_face.current_emotion, "focus")
        self.assertEqual(len(self.engine.event_log), 1)
        self.assertEqual(self.engine.event_log[0], (1, "SESSION_START"))

    def test_fidget_escalation_in_engine(self):
        self.engine.start_focus()
        # 1st Fidget
        self.engine.handle_event("FIDGET")
        self.assertEqual(self.engine.fidget_count, 1)
        self.assertEqual(self.mock_face.current_emotion, "side_eye")
        # 1st fidget in gentle mode has no words
        self.assertEqual(len(self.mock_face.speeches), 1)  # only SESSION_START spoke

        # 2nd Fidget
        self.engine.handle_event("FIDGET")
        self.assertEqual(self.engine.fidget_count, 2)
        self.assertIn("Almost there", self.mock_face.last_speech)

        # 3rd Fidget
        self.engine.handle_event("FIDGET")
        self.assertEqual(self.engine.fidget_count, 3)
        self.assertIn("restless", self.mock_face.last_speech.lower())

    def test_sensor_toggles_effective_immediately(self):
        self.engine.start_focus()
        # Turn off motion sensor
        self.engine.set_sensor_enabled("motion", False)
        prev_log_len = len(self.engine.event_log)
        self.engine.handle_event("FIDGET")
        self.engine.handle_event("SEAT_LEAVE")
        self.assertEqual(len(self.engine.event_log), prev_log_len)  # ignored!

        # Turn off tab switch sensor
        self.engine.set_sensor_enabled("tab_switch", False)
        self.engine.handle_event("TAB_SWITCH")
        self.assertEqual(len(self.engine.event_log), prev_log_len)  # ignored!

        # Turn off phone sensor
        self.engine.set_sensor_enabled("phone", False)
        self.engine.handle_event("PHONE")
        self.assertEqual(len(self.engine.event_log), prev_log_len)  # ignored!

        # Re-enable phone sensor
        self.engine.set_sensor_enabled("phone", True)
        self.engine.handle_event("PHONE")
        self.assertEqual(len(self.engine.event_log), prev_log_len + 1)

    def test_demo_mode_timing(self):
        self.engine.set_demo_mode(True)
        self.assertEqual(self.engine.focus_duration, 60)
        self.assertEqual(self.engine.break_duration, 15)

        self.engine.start_focus()
        self.assertEqual(self.engine.remaining_seconds, 60)

        # Tick 60 times
        for _ in range(60):
            self.engine.tick()

        # Should now be in break state
        self.assertEqual(self.engine.state, "break")
        self.assertEqual(self.engine.remaining_seconds, 15)

        # Tick 15 times
        for _ in range(15):
            self.engine.tick()

        # Should now be idle and triggered summary
        self.assertEqual(self.engine.state, "idle")
        self.assertEqual(len(self.summary_logs), 1)

    def test_take_break_now_always_works(self):
        self.engine.start_focus()
        self.engine.take_break()
        self.assertEqual(self.engine.state, "break")
        self.assertEqual(self.mock_face.current_emotion, "happy")
        self.assertIn("Break time. Your call.", self.mock_face.last_speech)


class TestAssistant(unittest.TestCase):
    """Verifies AssistantBrain natural language command handling."""

    def setUp(self):
        self.mock_face = MockFace()
        self.engine = Engine(face=self.mock_face)
        self.brain = assistant.AssistantBrain(self.engine)

    def test_wake_up_hi_esp(self):
        # Before waking up
        resp = self.brain.process_message("hello")
        self.assertIn("Hi ESP", resp)

        # Waking up
        resp = self.brain.process_message("Hi ESP")
        self.assertTrue(self.brain.is_awake)
        self.assertEqual(self.mock_face.current_emotion, "happy")
        self.assertIn("awake", resp.lower())

    def test_start_focus_and_break_commands(self):
        self.brain.process_message("Hi ESP")
        resp = self.brain.process_message("start focus")
        self.assertEqual(self.engine.state, "focus")
        self.assertIn("focus session", resp.lower())

        resp = self.brain.process_message("take a break now")
        self.assertEqual(self.engine.state, "break")
        self.assertIn("break time", resp.lower())

    def test_how_am_i_doing(self):
        self.brain.process_message("Hi ESP")
        self.brain.process_message("start focus")
        self.engine.handle_event("FIDGET")
        self.engine.handle_event("TAB_SWITCH")

        resp = self.brain.process_message("how am I doing?")
        self.assertIn("fidget", resp)
        self.assertIn("tab switch", resp)
        self.assertIn("doing well", resp.lower())

    def test_utility_commands(self):
        self.brain.process_message("Hi ESP")
        v_up = self.brain.process_message("volume up")
        self.assertIn("Volume increased", v_up)

        w = self.brain.process_message("weather")
        self.assertIn("forecast", w.lower())

        m = self.brain.process_message("music")
        self.assertIn("beats", m.lower())


if __name__ == "__main__":
    unittest.main()
