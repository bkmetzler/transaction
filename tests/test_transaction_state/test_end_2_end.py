import pytest

from transaction import transaction
from transaction import TransactionState

# from transaction.helpers import get_class

executed: list[tuple[str, int]] = []
rolled_back: list[tuple[str, int]] = []


@transaction
def func1(i: int) -> int:
    return i


@func1.rollback
def func1_rollback(i: int) -> int:
    return i


def func1_except(i: int) -> int:
    raise ValueError("func1_exception raised")


@transaction
async def afunc1(i: int) -> int:
    return i


@afunc1.rollback
async def afunc1_rollback(i: int) -> int:
    return i


async def afunc1_except(i: int) -> int:
    raise ValueError("func1_exception raised")


class StaticExample:
    @transaction
    def do(x: int) -> int:  # noqa: N805
        executed.append(("static", x))
        return x

    @do.rollback
    def undo(self, x: int) -> bool:
        rolled_back.append(("static", x))
        return True


class ClassExample:
    @classmethod
    @transaction
    def do(cls, x: int) -> int:
        executed.append((cls.__name__, x))
        return x

    @staticmethod
    def undo(x: int) -> bool:
        rolled_back.append(("class", x))
        return True


class InstanceExample:
    @transaction
    def do(self, k: float) -> float:
        return k

    @do.rollback
    def undo(self, k: float) -> bool:
        return True


@pytest.mark.parametrize(
    "class_type, func, arg, expected",
    [
        (None, func1, 10, 10),
        (None, StaticExample.do, 3, 3),
        (ClassExample, ClassExample.do, "hi", "hi"),
        (InstanceExample, InstanceExample().do, 3.14, 3.14),
    ],
)
def test_sync_transactional_functions(class_type, func, arg, expected):
    executed.clear()
    rolled_back.clear()

    # Working FunctionType.REGULAR_FUNCTION
    # Working FunctionType.STATIC_METHOD
    # with TransactionState():
    #     result = func(arg)
    #     assert result == expected

    # Working FunctionType.CLASS_METHOD
    with TransactionState():
        if class_type:
            result = func(class_type, arg)
        else:
            result = func(arg)
        assert result == expected


#
# @pytest.mark.parametrize(
#     "func, arg, expected_exception",
#     [
#         (func1_except, 5, ValueError),
#     ],
# )
# def test_sync_transactional_exceptions(func, arg, expected_exception):
#     with pytest.raises(expected_exception):
#         with TransactionState():
#             func(arg)
#
#
# # --- Asynchronous transactional function tests ---
#
#
# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "func, arg, expected",
#     [
#         (afunc1, 42, 42),
#     ],
# )
# async def test_async_transactional_functions(func, arg, expected):
#     async with TransactionState():
#         result = await func(arg)
#         assert result == expected
#
#
# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "func, arg, expected_exception",
#     [
#         (afunc1_except, 7, ValueError),
#     ],
# )
# async def test_async_transactional_exceptions(func, arg, expected_exception):
#     with pytest.raises(expected_exception):
#         async with TransactionState():
#             await func(arg)
