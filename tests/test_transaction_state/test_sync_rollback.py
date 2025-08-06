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
    assert state.stack[0].to_dict() == {
        "args": (),
        "exception": None,
        "kwargs": {},
        "name": "dummy",
        "rollback_func": "test_sync_rollback.rollback_func",
        "rolled_back": True,
    }
