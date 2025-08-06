import pytest

from transaction.classes.function_call import FunctionCall


def test_str_representation() -> None:
    call = FunctionCall(name="foo", args=(1,), kwargs={})
    assert str(call) == "foo(args=(1,), kwargs={})"


@pytest.mark.asyncio
async def test_rollback_no_function() -> None:  # type: ignore[return-value]
    call = FunctionCall(name="foo", args=(), kwargs={})
    with pytest.raises(RuntimeError, match="No rollback function"):
        await call.rollback()
    assert call.exception is not None


@pytest.mark.asyncio
async def test_rollback_classmethod_awaitable() -> None:  # type: ignore[return-value]
    class Handler:
        called_with: tuple[int, ...] | None = None

        @classmethod
        def rollback(cls, *nums: int):
            async def inner() -> None:
                cls.called_with = nums

            return inner()

    call = FunctionCall(
        name="do",
        args=(1, 2),
        kwargs={},
        rollback_func=Handler.rollback,
    )
    await call.rollback()
    assert call.rolled_back is True
    assert Handler.called_with[1:] == (1, 2)


def test_json_and_pickle_roundtrip() -> None:
    call = FunctionCall(name="foo", args=(1, 2), kwargs={})
    json_str = call.to_json()
    call_from_json = FunctionCall.from_json(json_str)
    assert call_from_json.name == "foo"

    pickled = call.to_pickle()
    unpickled = FunctionCall.from_pickle(pickled)
    assert unpickled.name == "foo"
