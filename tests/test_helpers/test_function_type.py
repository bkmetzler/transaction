from transaction.helpers import FunctionType


def test_is_supported_identifies_unsupported_types() -> None:
    unsupported = [
        FunctionType.LAMBDA_FUNCTION,
        FunctionType.PARTIAL_FUNCTION,
        FunctionType.GENERATOR_FUNCTION,
        FunctionType.BUILTIN_FUNCTION,
    ]
    for func_type in unsupported:
        assert not func_type.is_supported()


def test_is_supported_allows_unknown_type() -> None:
    assert FunctionType.UNKNOWN.is_supported()


def test_is_callable_identifies_callable_types() -> None:
    callable_types = [
        FunctionType.ASYNC_FUNCTION,
        FunctionType.COROUTINE_FUNCTION,
        FunctionType.INSTANCE_METHOD,
        FunctionType.REGULAR_FUNCTION,
    ]
    for func_type in callable_types:
        assert func_type.is_callable()
