from __future__ import annotations

from transaction import transaction
from transaction import TransactionState


def test_example_2() -> None:
    executed = {"rollback_int": False, "rollback_str": False}

    @transaction
    def step_int(i: int) -> int:
        return i

    @step_int.rollback
    def rollback_step_int(i: int) -> bool:
        executed["rollback_int"] = True
        return True

    @transaction
    def step_str(j: str) -> str:
        return j

    @step_str.rollback
    def rollback_step_str(j: str) -> bool:
        executed["rollback_str"] = True
        return True

    with TransactionState() as state:
        assert step_int(1) == 1
        assert step_str("2") == "2"

    assert len(state.stack) == 2
    assert executed == {"rollback_int": False, "rollback_str": False}
