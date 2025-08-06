from transaction.classes.transaction_state import TransactionState


def test_get_current_returns_state() -> None:
    token = TransactionState._current_state.set(None)
    try:
        assert TransactionState.get_current() is None
        with TransactionState() as state:
            assert TransactionState.get_current() is state
        assert TransactionState.get_current() is None
    finally:
        TransactionState._current_state.reset(token)
