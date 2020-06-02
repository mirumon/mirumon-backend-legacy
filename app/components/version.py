import toml


def get_app_version() -> str:
    with open("pyproject.toml") as pyproject:
        file_contents = pyproject.read()

    return toml.loads(file_contents)["tool"]["poetry"]["version"]