"""Typings for "private" pytest package."""

from _pytest.capture import CaptureManager
from _pytest.terminal import TerminalReporter

__all__ = (
    # pytest internals
    "TerminalReporter",
    "CaptureManager",
)
