import pytest

from transaction import transaction
from transaction.classes.transaction_state import TransactionState

called = []


@transaction
async def do_async(x):
    called.append(f"do({x})")


@do_async.rollback
async def rollback_async(x):
    called.append(f"undo({x})")


@pytest.mark.asyncio
async def test_async_transaction_rollback():
    try:
        async with TransactionState(reraise=True):
            await do_async(1)
            await do_async(2)
            raise RuntimeError("fail async")
    except RuntimeError:
        pass

    assert called == ["do(1)", "do(2)", "undo(2)", "undo(1)"]
