from __future__ import annotations

import pytest

from transaction import transaction
from transaction import TransactionState


@pytest.mark.asyncio
async def test_example_5() -> None:
    calls: list[int] = []

    @transaction
    def step1(i: int) -> int:
        calls.append(i)
        return i

    @step1.rollback
    def step1_rollback(i: int) -> bool:
        calls.append(-i)
        return True

    async with TransactionState() as state:
        step1(1)
        step1(2)
        step1(3)

    assert calls == [1, 2, 3]
    assert len(state.stack) == 3
