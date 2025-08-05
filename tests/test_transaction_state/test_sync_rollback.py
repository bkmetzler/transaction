import pytest

from transaction.classes.function_call import FunctionCall
from transaction.classes.transaction_state import TransactionState


@pytest.mark.asyncio
async def test_sync_rollback_with_running_loop():
    ran = []

    def rollback_func() -> None:
        ran.append(True)

    state = TransactionState()
    state.record_call(FunctionCall(name="dummy", args=(), kwargs={}, rollback_func=rollback_func))

    state.rollback()

    assert ran == [True]
    assert state.stack == []
