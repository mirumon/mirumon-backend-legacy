import re

from app.common.versions import get_app_version


def test_app_version_regex() -> None:
    version = get_app_version()
    assert re.match(r"\d+.\d+.\d+", version)
