import functools
import inspect

import pytest

from transaction.helpers import FunctionType
from transaction.helpers import get_class
from transaction.helpers import get_function_type


def test_get_function_type_variants() -> None:
    def sample(a: int, b: int) -> int:
        return a + b

    partial_func = functools.partial(sample, 1)
    assert get_function_type(None, partial_func) is FunctionType.PARTIAL_FUNCTION

    assert get_function_type(None, len) is FunctionType.BUILTIN_FUNCTION

    async def coro() -> None:
        pass

    c = coro()
    try:
        assert get_function_type(None, c) is FunctionType.COROUTINE_FUNCTION
    finally:
        c.close()

    def gen() -> int:
        yield 1

    assert get_function_type(None, gen) is FunctionType.GENERATOR_FUNCTION

    class Demo:
        def inst(self) -> None:
            pass

        @classmethod
        def cls(cls) -> None:
            pass

    demo = Demo()
    assert get_function_type(demo, demo.inst) is FunctionType.INSTANCE_METHOD
    assert get_function_type(Demo, Demo.cls) is FunctionType.CLASS_METHOD

    assert get_function_type(None, lambda x: x) is FunctionType.LAMBDA_FUNCTION

    assert get_function_type(None, object()) is FunctionType.UNKNOWN


def test_get_function_type_class_hierarchy(monkeypatch: pytest.MonkeyPatch) -> None:
    class Container:
        @staticmethod
        def sm() -> None:
            pass

        @classmethod
        def cm(cls) -> None:
            pass

        def reg(self) -> None:
            pass

    class Dummy:
        def __init__(self, name: str) -> None:
            self.__name__ = name

    monkeypatch.setattr(inspect, "isfunction", lambda obj: isinstance(obj, Dummy))
    monkeypatch.setattr(inspect, "iscoroutinefunction", lambda obj: False)
    monkeypatch.setattr(inspect, "iscoroutine", lambda obj: False)
    monkeypatch.setattr(inspect, "isgeneratorfunction", lambda obj: False)
    monkeypatch.setattr(inspect, "ismethod", lambda obj: False)

    assert get_function_type(Container, Dummy("sm")) is FunctionType.STATIC_METHOD
    assert get_function_type(Container, Dummy("cm")) is FunctionType.CLASS_METHOD
    assert get_function_type(Container, Dummy("reg")) is FunctionType.REGULAR_FUNCTION


def test_get_class() -> None:
    def sample() -> None:
        pass

    assert get_class(sample) is sample.__class__
