from collections.abc import Callable
from contextlib import nullcontext

import pytest

from transaction import transaction
from transaction import TransactionState


executed: list[tuple[str, int]] = []
rolled_back: list[tuple[str, int]] = []


@transaction
def func1(i: int) -> int:
    executed.append(("func1", i))
    return i


@func1.rollback
def func1_rollback(i: int) -> bool:
    rolled_back.append(("func1_rollback", i))
    return True


@transaction
def func2(i: int) -> int:
    executed.append(("func2", i))
    raise Exception(f"func2 exception {i}")


@func2.rollback
def func2_rollback(i: int) -> bool:
    rolled_back.append(("func2_rollback", i))
    return True


@transaction
def func3(i: int) -> int:
    executed.append(("func3", i))
    if i > 1:
        raise Exception(f"func3 {i}")
    return i


@func3.rollback
def func3_rollback(i: int) -> bool:
    rolled_back.append(("func3_rollback", i))
    return True


@transaction
def func4(i: int) -> int:
    executed.append(("func4", i))
    if i == 2:
        raise Exception(f"func4 {i}")

    return i


@func4.rollback
def func4_rollback(i: int) -> bool:
    rolled_back.append(("func4", i))
    raise Exception(f"func4_rollback {i}")


@pytest.mark.parametrize(
    "context,reraise,func,vars1,vars2,expected_executed,expected_rolledback",
    [
        (nullcontext(), False, func1, 1, 1, [("func1", 1), ("func1", 1)], []),
        (pytest.raises(Exception), True, func2, 1, 1, [("func2", 1)], [("func2_rollback", 1)]),
        (
            pytest.raises(Exception),
            True,
            func3,
            1,
            2,
            [("func3", 1), ("func3", 2)],
            [("func3_rollback", 1), ("func3_rollback", 2)],
        ),
        (pytest.raises(Exception), True, func4, 1, 2, [("func4", 1), ("func4", 2)], [("func4", 2)]),
    ],
)
def test_rollback(
    context: nullcontext | None,
    reraise: bool,
    func: Callable,
    vars1: int,
    vars2: int,
    expected_executed: list,
    expected_rolledback: list,
) -> None:
    executed.clear()
    rolled_back.clear()

    with context:
        with TransactionState(reraise=reraise):
            func(vars1)
            func(vars2)
    assert sorted(executed) == sorted(expected_executed)
    assert sorted(rolled_back) == sorted(expected_rolledback)
