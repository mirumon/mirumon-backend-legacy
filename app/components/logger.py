import json
import logging

from loguru import logger
from loguru._defaults import LOGURU_FORMAT  # noqa: WPS436


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        logger_opt = logger.opt(depth=7, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def format_record(record: dict) -> str:
    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = json.dumps(
            record["extra"]["payload"], indent=4, ensure_ascii=False
        )
        format_string = "".join((format_string, "\n<level>{extra[payload]}</level>"))
    format_string = "".join((format_string, "{exception}\n"))
    return format_string
