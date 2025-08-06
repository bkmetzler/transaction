from __future__ import annotations

from transaction import transaction
from transaction import TransactionState


@transaction
def step1(i: int) -> int:
    return i


@step1.rollback
def step1_rollback(i: int) -> bool:
    return True


def test_example_6() -> None:
    with TransactionState() as state:
        step1(1)
        step1(2)
        step1(3)
        export_json_str = state.export_history()

    with TransactionState.import_history(export_json_str) as imported_state:
        step1(4)
        step1(5)
        step1(6)

    assert len(state.stack) == 3
    assert len(imported_state.stack) == 6
