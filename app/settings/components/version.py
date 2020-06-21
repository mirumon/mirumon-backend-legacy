"""Get application actual version for usage in OpenAPI specification or other docs."""

import toml


def get_app_version() -> str:
    """Read application version from pyproject.toml file."""
    with open("pyproject.toml") as pyproject:
        file_contents = pyproject.read()

    return toml.loads(file_contents)["tool"]["poetry"]["version"]
