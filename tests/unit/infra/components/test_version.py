import re

from mirumon.infra.components.version import get_app_version


def test_app_version_from_toml() -> None:
    version = get_app_version()
    assert re.match(r"\d+.\d+.\d+", version)
