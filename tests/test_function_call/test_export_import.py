from transaction import FunctionCall
from transaction import TransactionState


def test_transaction_begin_end_and_rollback():
    calls = []

    def step(x):
        calls.append(f"do({x})")

    def rollback(x):
        calls.append(f"undo({x})")

    call1 = FunctionCall("step", (1,), {}, rollback)
    call2 = FunctionCall("step", (2,), {}, rollback)

    with TransactionState() as txn:
        txn.record_call(call1)
        txn.record_call(call2)

        # rollback manually
        import asyncio

        asyncio.run(txn.rollback())

    assert calls == ["undo(2)", "undo(1)"]
