import pkg_resources


def get_app_version() -> str:
    return pkg_resources.get_distribution("mirumon-backend").version
