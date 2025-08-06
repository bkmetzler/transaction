import pytest

from transaction.classes.function_call import FunctionCall
from transaction.classes.transaction_state import TransactionState


@pytest.mark.asyncio
async def test_rollback_in_running_loop() -> None:  # type: ignore[return-value]
    def failing() -> None:
        raise ValueError("fail")

    call = FunctionCall(name="f", args=(), kwargs={}, rollback_func=failing)
    state = TransactionState()
    state.record_call(call)

    with pytest.raises(ValueError, match="fail"):
        state.rollback()
