import json

import pytest

from transaction import transaction
from transaction import TransactionState


executed: list[tuple[str, int]] = []
rolled_back: list[tuple[str, int]] = []


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


@pytest.mark.parametrize(
    "func, arg, context",
    [
        (func1_except, 5, pytest.raises(ValueError)),
    ],
)
def test_sync_transactional_exceptions(func, arg, context):
    with context:
        with TransactionState():
            func(arg)


# --- Asynchronous transactional function tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "func, arg, expected",
    [
        (afunc1, 42, 42),
    ],
)
async def test_async_transactional_functions(func, arg, expected):
    async with TransactionState():
        result = await func(arg)
        assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "func, arg, context",
    [
        (afunc1_except, 7, pytest.raises(ValueError)),
    ],
)
async def test_async_transactional_exceptions(func, arg, context):
    executed.clear()
    rolled_back.clear()

    with context:
        async with TransactionState() as state:
            await func(arg)
            json_str = state.export_history()

        data = json.loads(json_str)
        assert data == []
