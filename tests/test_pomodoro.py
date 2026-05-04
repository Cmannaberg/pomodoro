"""Unit tests for pomodoro.py"""

import pytest
import sys
import os

# Ensure the project root is on sys.path regardless of how pytest is invoked.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pomodoro import PomodoroSession, _format_time


# ---------------------------------------------------------------------------
# PomodoroSession — construction
# ---------------------------------------------------------------------------

class TestPomodoroSessionDefaults:
    def test_default_work_minutes(self):
        s = PomodoroSession()
        assert s.work_minutes == 25

    def test_default_short_break_minutes(self):
        s = PomodoroSession()
        assert s.short_break_minutes == 5

    def test_default_long_break_minutes(self):
        s = PomodoroSession()
        assert s.long_break_minutes == 15

    def test_default_sessions_before_long_break(self):
        s = PomodoroSession()
        assert s.sessions_before_long_break == 4

    def test_initial_completed_sessions_is_zero(self):
        s = PomodoroSession()
        assert s.completed_sessions == 0


class TestPomodoroSessionCustomValues:
    def test_custom_work_minutes(self):
        s = PomodoroSession(work_minutes=50)
        assert s.work_minutes == 50

    def test_custom_short_break(self):
        s = PomodoroSession(short_break_minutes=10)
        assert s.short_break_minutes == 10

    def test_custom_long_break(self):
        s = PomodoroSession(long_break_minutes=30)
        assert s.long_break_minutes == 30

    def test_custom_sessions_before_long_break(self):
        s = PomodoroSession(sessions_before_long_break=2)
        assert s.sessions_before_long_break == 2


class TestPomodoroSessionValidation:
    @pytest.mark.parametrize("kwarg", ["work_minutes", "short_break_minutes", "long_break_minutes", "sessions_before_long_break"])
    def test_zero_value_raises(self, kwarg):
        with pytest.raises(ValueError):
            PomodoroSession(**{kwarg: 0})

    @pytest.mark.parametrize("kwarg", ["work_minutes", "short_break_minutes", "long_break_minutes", "sessions_before_long_break"])
    def test_negative_value_raises(self, kwarg):
        with pytest.raises(ValueError):
            PomodoroSession(**{kwarg: -1})


# ---------------------------------------------------------------------------
# PomodoroSession — session tracking
# ---------------------------------------------------------------------------

class TestRecordCompletedSession:
    def test_increments_counter(self):
        s = PomodoroSession()
        s.record_completed_session()
        assert s.completed_sessions == 1

    def test_increments_multiple_times(self):
        s = PomodoroSession(sessions_before_long_break=4)
        for _ in range(7):
            s.record_completed_session()
        assert s.completed_sessions == 7


# ---------------------------------------------------------------------------
# PomodoroSession — break scheduling
# ---------------------------------------------------------------------------

class TestNextBreakDuration:
    def test_first_break_is_short(self):
        s = PomodoroSession()
        # No sessions completed yet; next break (after session #1) is short.
        assert s.next_break_duration() == s.short_break_minutes

    def test_fourth_break_is_long(self):
        s = PomodoroSession(sessions_before_long_break=4)
        # After 3 completed sessions, the 4th session triggers a long break.
        for _ in range(3):
            s.record_completed_session()
        assert s.next_break_duration() == s.long_break_minutes

    def test_long_break_every_n_sessions(self):
        s = PomodoroSession(sessions_before_long_break=2)
        # Session 1 → short break
        assert s.next_break_duration() == s.short_break_minutes
        s.record_completed_session()
        # Session 2 → long break
        assert s.next_break_duration() == s.long_break_minutes
        s.record_completed_session()
        # Session 3 → short break (cycle resets)
        assert s.next_break_duration() == s.short_break_minutes

    def test_is_long_break_next_false_initially(self):
        s = PomodoroSession()
        assert not s.is_long_break_next()

    def test_is_long_break_next_true_before_fourth(self):
        s = PomodoroSession(sessions_before_long_break=4)
        for _ in range(3):
            s.record_completed_session()
        assert s.is_long_break_next()


# ---------------------------------------------------------------------------
# _format_time helper
# ---------------------------------------------------------------------------

class TestFormatTime:
    def test_zero_seconds(self):
        assert _format_time(0) == "00:00"

    def test_one_minute(self):
        assert _format_time(60) == "01:00"

    def test_twenty_five_minutes(self):
        assert _format_time(25 * 60) == "25:00"

    def test_partial_minute(self):
        assert _format_time(90) == "01:30"

    def test_negative_clamps_to_zero(self):
        assert _format_time(-5) == "00:00"
