"""Classes and functions to customize logs."""
import logging
from pprint import pformat

from loguru import Record, logger
from loguru._defaults import LOGURU_FORMAT  # noqa: WPS436

MAX_PAYLOAD_WIDTH = 88


class InterceptHandler(logging.Handler):
    """
    Logging handler interceptor from loguru documentation.

    For more info see https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging  # noqa: E501
    """

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        """Log the specified logging record by loguru logger."""
        try:
            # Get corresponding Loguru level if it exists
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def format_record(record: Record) -> str:
    """
    Customize format for loguru loggers.

    Uses pformat for log any data like request or
    response body during debug. Works with logging if loguru handler it.

    Example:
    >>> payload = [
    >>>     {"users":[{"name": "Nick", "age": 87, "is_active": True},
    >>>     {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    >>> logger.bind(payload=payload).debug("users payload")
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"],
            indent=4,
            compact=True,
            width=MAX_PAYLOAD_WIDTH,
        )
        return "{0}{1}{2}".format(
            LOGURU_FORMAT,
            "\n<level>{extra[payload]}</level>",
            "{exception}\n",
        )

    return "{0}{1}{2}".format(LOGURU_FORMAT, "", "{exception}\n")
