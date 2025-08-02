from transaction import transaction
from transaction.classes.transaction_state import TransactionState

called = []


@transaction
def do_something(x):
    called.append(f"do({x})")


@do_something.rollback
def rollback_something(x):
    called.append(f"undo({x})")


def test_sync_transaction_rollback():
    try:
        with TransactionState(reraise=True):
            do_something(1)
            do_something(2)
            raise RuntimeError("fail")
    except RuntimeError:
        pass

    assert called == ["do(1)", "do(2)", "undo(2)", "undo(1)"]
