import pytest

from transaction.classes.transaction_state import TransactionState
from transaction.decorator import transaction


executed: list[tuple[str, int]] = []
rolled_back: list[tuple[str, int]] = []


class StaticExample:
    @transaction
    @staticmethod
    def do(x: int) -> None:
        executed.append(("static", x))

    @staticmethod
    @do.rollback
    def undo(x: int) -> None:
        rolled_back.append(("static", x))


class ClassExample:
    @transaction
    @classmethod
    def do(cls, x: int) -> None:
        executed.append((cls.__name__, x))

    @classmethod
    @do.rollback
    def undo(cls, x: int) -> None:
        rolled_back.append((cls.__name__, x))


def test_transaction_staticmethod() -> None:
    executed.clear()
    rolled_back.clear()

    with pytest.raises(RuntimeError):
        with TransactionState():
            StaticExample.do(1)
            raise RuntimeError("fail")

    assert executed == [("static", 1)]
    assert rolled_back == [("static", 1)]


def test_transaction_classmethod() -> None:
    executed.clear()
    rolled_back.clear()

    with pytest.raises(RuntimeError):
        with TransactionState():
            ClassExample.do(2)
            raise RuntimeError("fail")

    assert executed == [("ClassExample", 2)]
    assert rolled_back == [("ClassExample", 2)]

