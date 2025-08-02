import pytest

from transaction.classes.function_call import FunctionCall


def dummy_func(a, b):
    return a + b


def dummy_rollback(a, b):
    dummy_rollback.called.append((a, b))


dummy_rollback.called = []


@pytest.mark.asyncio
async def test_function_call_rollback_success():
    call = FunctionCall(
        name="dummy_func",
        args=(1, 2),
        kwargs={},
        rollback_func=dummy_rollback,
    )

    await call.rollback()
    assert call.rolled_back is True
    assert call.exception is None
    assert dummy_rollback.called == [(1, 2)]


@pytest.mark.asyncio
async def test_function_call_rollback_failure():
    def failing_rollback(x):
        raise ValueError("Rollback failure")

    call = FunctionCall(
        name="fail_test",
        args=(10,),
        kwargs={},
        rollback_func=failing_rollback,
    )

    with pytest.raises(ValueError, match="Rollback failure"):
        await call.rollback()

    assert call.rolled_back is False
    assert "ValueError" in call.exception
