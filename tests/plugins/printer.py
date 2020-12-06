"""Fixtures for print logs when pytest running."""
import time
from threading import Event
from typing import Any, Callable, NewType

import pytest

from tests.plugins.typing import CaptureManager, TerminalReporter

# TODO: replace by plugin from pypi
# typing for printer function
Printer = NewType("Printer", Callable)  # type: ignore


def _do_nothing(*_: Any) -> None:  # type: ignore
    """Do nothing."""


def _create_printer_function(  # type: ignore
    terminal_reporter: TerminalReporter,
    capture_manager: CaptureManager,
) -> Callable[..., None]:
    was_called = Event()
    start_time = time.monotonic()

    def factory(msg: str, *_: Any) -> None:  # type: ignore
        """Print messages with time duration."""
        new_line = ""
        # in case of the first call we don't have a new empty line
        if not was_called.is_set():
            new_line = "\n"
            was_called.set()

        delta = time.monotonic() - start_time
        log_line = "{0}{1:.3f}s :: {2}\n".format(new_line, delta, msg)
        with capture_manager.global_and_fixture_disabled():
            terminal_reporter.write(log_line)

    return factory


@pytest.fixture(scope="session")
def printer(request) -> Printer:  # type: ignore
    """Print progress steps in verbose mode.

    Create public function `printer` for usage in any test helpers, not only fixtures.
    Based on:
    https://github.com/pytest-dev/pytest-print/blob/master/src/pytest_print/__init__.py

    Args:
        request: request object for pytest fixtures

    Returns:
        Function for printing in pytest session log.
    """

    terminal_reporter = request.config.pluginmanager.getplugin("terminalreporter")
    capture_manager = request.config.pluginmanager.get_plugin("capturemanager")

    use_fake_printer = (
        request.config.getoption("verbose") <= 0 or terminal_reporter is None
    )

    if use_fake_printer:
        return Printer(_do_nothing)

    return Printer(_create_printer_function(terminal_reporter, capture_manager))
