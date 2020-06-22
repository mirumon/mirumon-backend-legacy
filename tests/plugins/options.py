import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--docker", action="store_true", default=True, help="run docker services"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--docker"):
        docker_services = ["tests.plugins.docker",
                           "tests.services.postgres", ]  # "tests.fixtures.services.redis"]
        config.pluginmanager.register("tests.plugins.docker")

    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_report_header(config):
    return "docker: " + str(config.getoption("--docker"))

