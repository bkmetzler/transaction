from __future__ import annotations

from transaction import transaction
from transaction import TransactionState


def test_example_1() -> None:
    events: list[str] = []

    @transaction
    def step(i: int) -> int:
        events.append(f"step:{i}")
        return i

    @step.rollback
    def rollback_step(i: int) -> bool:
        events.append(f"rollback_step:{i}")
        return True

    @transaction
    def raise_except(j: str) -> str:
        events.append(f"raise_except:{j}")
        raise Exception("Random Exception")

    @raise_except.rollback
    def undo_raise_exception(j: str) -> bool:
        events.append(f"undo_raise_exception:{j}")
        return True

    with TransactionState(reraise=False):
        step(1)
        step(2)
        step(3)
        raise_except("random string")

    assert events == [
        "step:1",
        "step:2",
        "step:3",
        "raise_except:random string",
        "undo_raise_exception:random string",
        "rollback_step:3",
        "rollback_step:2",
        "rollback_step:1",
    ]
