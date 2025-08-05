from contextlib import nullcontext
from typing import Callable

import pytest
from pytest_lazyfixture import lazy_fixture

from transaction import TransactionState, transaction

executed: list[tuple[str, int]] = []
rolled_back: list[tuple[str, int]] = []


@transaction
def func1(i: int) -> int:
    executed.append(("func1", i))
    return i

@func1.rollback
def func1_rollback(i: int) -> bool:
    rolled_back.append(("func1", i))
    return True


@transaction
def func2(i: int) -> int:
    executed.append(("func2", i))
    raise Exception(f"func2 exception {i}")

@func2.rollback
def func2_rollback(i: int) -> bool:
    rolled_back.append(("func2", i))
    return True


@transaction
def func3(i: int) -> int:
    executed.append(("func3", i))
    return i

@func3.rollback
def func3_rollback(i: int) -> bool:
    rolled_back.append(("func3", i))
    return False


@transaction
def func4(i: int) -> int:
    executed.append(("func4", i))
    if i == 2:
        raise Exception(f"func4 {i}")

    return i

@func4.rollback
def func4_rollback(i: int) -> bool:
    rolled_back.append(("func2", i))
    raise Exception(f"func4_rollback {i}")



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "context,reraise,func,vars1,vars2,expected_executed,expected_rolledback",
    [
        # (nullcontext(), False, func1, 1, 1, [('func1', 1), ('func1', 1)], []),
        (pytest.raises(Exception), True, func2, 1, 1, [('func2', 1)], [('func2_rollback', 1)]), # TODO: Need to figure out why rollback isn't being logged
        # (nullcontext(), True, func3, 1, 1, [('func2', 1), ('func2', 1)], []), # TODO: Need to figure out why rollback isn't being logged
        # (pytest.raises(Exception), True, func4, 1, 2, [('func4', 1), ('func4', 2)], []), # TODO: Need to figure out why rollback isn't being logged
    ],
)
async def test_rollback(context: nullcontext | None, reraise: bool, func: Callable, vars1: int, vars2: int, expected_executed: list, expected_rolledback: list) -> None:
    executed.clear()
    rolled_back.clear()

    with context:
        with TransactionState(reraise=reraise):
            func(vars1)
            func(vars2)
    assert sorted(executed) == sorted(expected_executed)
    assert sorted(rolled_back) == sorted(expected_rolledback)




#
# @pytest.mark.parametrize(
#     "context, class_type, func, arg, expected",
#     [
#         (nullcontext(), None, func1, 10, 10),
#         (nullcontext(), None, StaticExample.do, 3, 3),
#         (nullcontext(), None, ClassExample.do, "hi", "hi"),
#         (nullcontext(), InstanceExample, InstanceExample().do, 3.14, 3.14),
#         (pytest.raises(ValueError), InstanceExample, InstanceExample().do_except, 3.14, 3.14)
#     ],
# )
# def test_sync_transactional_functions(context, class_type, func, arg, expected):
#     executed.clear()
#     rolled_back.clear()
#
#     with context:
#         with TransactionState():
#             if class_type:
#                 result = func(class_type, arg)
#             else:
#                 result = func(arg)
#             assert result == expected
