import pytest

from transaction.classes.transaction_state import TransactionState
from transaction.decorator import transaction

executed = []
rolled_back = []


@transaction
def do_something(x: int) -> int:
    executed.append(x)
    if x == 4:
        raise Exception("Boom!")
    return x * 2


@do_something.rollback
def undo_something(x: int) -> None:
    print(f"[DEBUG] Rolling back {x}")
    rolled_back.append(x)


def test_transaction_success():
    executed.clear()
    rolled_back.clear()

    with TransactionState(reraise=True):
        result = do_something(5)
        assert result == 10

    assert executed == [5]
    assert rolled_back == []


def test_transaction_decorator_with_error():
    executed.clear()
    rolled_back.clear()

    with pytest.raises(Exception, match="Boom!"):
        with TransactionState(reraise=True):
            do_something(1)
            do_something(4)  # Will raise

    assert executed == [1, 4]
    assert rolled_back == [4, 1]  # Rolled back in reverse order


def test_transaction_rollback_on_exception():
    executed.clear()
    rolled_back.clear()

    try:
        with TransactionState(reraise=False):
            do_something(7)
            raise RuntimeError("Boom!")
    except RuntimeError:
        pytest.fail("Should not re-raise with reraise=False")

    assert executed == [7]
    assert rolled_back == [7]


@pytest.mark.asyncio
async def test_transaction_rollback_metadata():
    executed.clear()
    rolled_back.clear()

    with TransactionState() as state:
        stack_length = 0
        try:
            do_something(3)
            do_something(2)
            stack_length = len(state.stack)
            raise Exception("Trigger rollback")
        except Exception:
            pass
        finally:
            await state.rollback_async()

        assert executed == [3, 2]
        assert rolled_back == [2, 3]
        assert stack_length == 2
