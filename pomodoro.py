"""
Pomodoro Timer
--------------
A command-line Pomodoro timer that helps you stay focused.

Default durations:
  Work session  : 25 minutes
  Short break   : 5 minutes
  Long break    : 15 minutes (after every 4 work sessions)
"""

import argparse
import sys
import time


# ---------------------------------------------------------------------------
# Core timer logic (testable without I/O side-effects)
# ---------------------------------------------------------------------------

class PomodoroSession:
    """Tracks state for a complete Pomodoro work session cycle."""

    DEFAULT_WORK_MINUTES = 25
    DEFAULT_SHORT_BREAK_MINUTES = 5
    DEFAULT_LONG_BREAK_MINUTES = 15
    DEFAULT_SESSIONS_BEFORE_LONG_BREAK = 4

    def __init__(
        self,
        work_minutes: int = DEFAULT_WORK_MINUTES,
        short_break_minutes: int = DEFAULT_SHORT_BREAK_MINUTES,
        long_break_minutes: int = DEFAULT_LONG_BREAK_MINUTES,
        sessions_before_long_break: int = DEFAULT_SESSIONS_BEFORE_LONG_BREAK,
    ):
        if work_minutes <= 0:
            raise ValueError("work_minutes must be positive")
        if short_break_minutes <= 0:
            raise ValueError("short_break_minutes must be positive")
        if long_break_minutes <= 0:
            raise ValueError("long_break_minutes must be positive")
        if sessions_before_long_break <= 0:
            raise ValueError("sessions_before_long_break must be positive")

        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes
        self.sessions_before_long_break = sessions_before_long_break

        self.completed_sessions: int = 0

    # ------------------------------------------------------------------
    # State helpers (no I/O)
    # ------------------------------------------------------------------

    def next_break_duration(self) -> int:
        """Return the break duration (in minutes) that follows the next work session."""
        if (self.completed_sessions + 1) % self.sessions_before_long_break == 0:
            return self.long_break_minutes
        return self.short_break_minutes

    def is_long_break_next(self) -> bool:
        """Return True when the next break will be a long break."""
        return self.next_break_duration() == self.long_break_minutes

    def record_completed_session(self) -> None:
        """Increment the completed session counter."""
        self.completed_sessions += 1


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _format_time(seconds: int) -> str:
    """Return a MM:SS string for the given number of seconds."""
    minutes, secs = divmod(max(seconds, 0), 60)
    return f"{minutes:02d}:{secs:02d}"


def _countdown(total_seconds: int, label: str) -> None:
    """Display a live countdown, updating the same terminal line each second."""
    for remaining in range(total_seconds, -1, -1):
        print(f"\r  {label}: {_format_time(remaining)}  ", end="", flush=True)
        if remaining > 0:
            time.sleep(1)
    print()  # newline after countdown finishes


def _notify(message: str) -> None:
    """Print a prominent notification message."""
    border = "=" * 50
    print(f"\n{border}")
    print(f"  {message}")
    print(f"{border}\n")


def _prompt_continue(prompt: str) -> bool:
    """Ask the user whether to continue; return False if they want to quit."""
    try:
        answer = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer not in {"q", "quit", "n", "no", "exit"}


# ---------------------------------------------------------------------------
# Main run loop
# ---------------------------------------------------------------------------

def run(session: PomodoroSession, *, skip_input: bool = False) -> None:
    """
    Execute the Pomodoro loop until the user quits.

    Parameters
    ----------
    session      : PomodoroSession instance that holds configuration and state.
    skip_input   : When True, skip all prompts (useful for automated tests).
    """
    _notify("Pomodoro Timer started! Press Ctrl+C at any time to quit.")

    try:
        while True:
            session_num = session.completed_sessions + 1
            print(f"Session #{session_num} — Work for {session.work_minutes} minute(s)")
            _countdown(session.work_minutes * 60, "Working")

            session.record_completed_session()
            _notify(f"Session #{session_num} complete! ({session.completed_sessions} total)")

            if session.completed_sessions % session.sessions_before_long_break == 0:
                break_label = "Long break"
                break_minutes = session.long_break_minutes
            else:
                break_label = "Short break"
                break_minutes = session.short_break_minutes

            print(f"{break_label} — {break_minutes} minute(s)")
            _countdown(break_minutes * 60, break_label)

            _notify("Break over!")

            if skip_input:
                break

            if not _prompt_continue("Start next session? [Enter / q to quit]: "):
                break

    except KeyboardInterrupt:
        print("\n\nQuitting — great work!")
        return

    print(f"\nCompleted {session.completed_sessions} Pomodoro session(s). Well done!")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Command-line Pomodoro timer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--work",
        type=int,
        default=PomodoroSession.DEFAULT_WORK_MINUTES,
        metavar="MINUTES",
        help="Work session duration in minutes",
    )
    parser.add_argument(
        "--short-break",
        type=int,
        default=PomodoroSession.DEFAULT_SHORT_BREAK_MINUTES,
        metavar="MINUTES",
        help="Short break duration in minutes",
    )
    parser.add_argument(
        "--long-break",
        type=int,
        default=PomodoroSession.DEFAULT_LONG_BREAK_MINUTES,
        metavar="MINUTES",
        help="Long break duration in minutes",
    )
    parser.add_argument(
        "--sessions",
        type=int,
        default=PomodoroSession.DEFAULT_SESSIONS_BEFORE_LONG_BREAK,
        metavar="N",
        help="Number of work sessions before a long break",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        session = PomodoroSession(
            work_minutes=args.work,
            short_break_minutes=args.short_break,
            long_break_minutes=args.long_break,
            sessions_before_long_break=args.sessions,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    run(session)
    return 0


if __name__ == "__main__":
    sys.exit(main())
