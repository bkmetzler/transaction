from typing import Callable

import pytest
from transaction import transaction

executed = []
rolled_back = []


@pytest.fixture
def static_example() -> "StaticExample":
    executed.clear()
    rolled_back.clear()
    
    class StaticExample:
        def __init__(self, *args, **kwargs):
            print(f"StaticExample {args} {kwargs}")
            return

        @transaction
        def do(x: int) -> int:  # noqa: N805
            executed.append(("static", x))
            return x

        @do.rollback
        def undo(self, x: int) -> bool:
            rolled_back.append(("static", x))
            return True

    return StaticExample

@pytest.fixture(scope="function")
def class_example() -> "ClassExample":
    executed.clear()
    rolled_back.clear()
    class ClassExample:
        def __init__(self, *args, **kwargs):
            print(f"ClassExample {args} {kwargs}")
            return

        @classmethod
        @transaction
        def do(cls, x: int) -> int:
            executed.append((cls.__name__, x))
            return x

        @staticmethod
        def undo(x: int) -> bool:
            rolled_back.append(("class", x))
            return True

    ClassExample.do.rollback(ClassExample.undo)
    return ClassExample


@pytest.fixture(scope="function")
def instance_example() -> "InstanceExample":
    executed.clear()
    rolled_back.clear()
    class InstanceExample:
        def __init__(self, *args, **kwargs):
            print(f"InstanceExample {args} {kwargs}")
            return

        @transaction
        def do(self, k: float) -> float:
            return k

        @do.rollback
        def undo(self, k: float) -> bool:
            return True

        @transaction
        def do_except(self, k: float) -> float:
            raise ValueError("Exception while running do_except")

        @do_except.rollback
        def do_except_rollback(self, k: float) -> float:
            return True
    return InstanceExample


@pytest.fixture
def function_example() -> Callable:
    executed.clear()
    rolled_back.clear()

    @transaction
    def func1(i: int) -> int:
        return i

    @func1.rollback
    def func1_rollback(i: int) -> int:
        return i

    return func1


@pytest.fixture
def function_exception_example(custom_exception: Exception) -> Callable:
    executed.clear()
    rolled_back.clear()

    @transaction
    def func1_exception(i: int) -> int:
        raise custom_exception

    @func1_exception.rollback
    def func1_exception_rollback(i: int) -> bool:
        return True

    return func1_exception


@pytest.fixture
def function_exception_rollback_failed_example() -> Callable:
    executed.clear()
    rolled_back.clear()

    @transaction
    def func1_exception(i: int) -> int:
        raise Exception("func1_example")

    @func1_exception.rollback
    def func1_exception_rollback(i: int) -> bool:
        return True

    return func1_exception
