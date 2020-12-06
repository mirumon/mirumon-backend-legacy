import pytest

pytest_plugins = [
    "tests.plugins.printer",
]


@pytest.fixture
def secret_key() -> str:
    return "test-secret-key"


@pytest.fixture
def shared_key() -> str:
    return "test-shared-key"


@pytest.fixture
def superuser_username() -> str:
    return "test-superuser-username"


@pytest.fixture
def superuser_password() -> str:
    return "test-superuser-password"
