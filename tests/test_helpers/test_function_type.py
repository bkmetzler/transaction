from transaction.helpers import FunctionType


def test_is_callable() -> None:
    assert FunctionType.REGULAR_FUNCTION.is_callable() is True
    assert FunctionType.CLASS_METHOD.is_callable() is False


def test_is_not_supported() -> None:
    assert FunctionType.LAMBDA_FUNCTION.is_not_supported() is False
    assert FunctionType.REGULAR_FUNCTION.is_not_supported() is True
