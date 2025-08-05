import pytest

class CustomException(Exception):
    pass


@pytest.fixture
def custom_exception() -> CustomException:
    return CustomException("Raise Custom Exception")