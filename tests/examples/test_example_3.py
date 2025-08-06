from __future__ import annotations

import pytest

from transaction import transaction
from transaction import TransactionState


@pytest.mark.asyncio
async def test_example_3() -> None:
    events: list[str] = []

    @transaction
    async def step(i: int) -> int:
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
    async def undo_raise_exception(j: str) -> bool:
        events.append(f"undo_raise_exception:{j}")
        return True

    class MyClass:
        @staticmethod
        @transaction
        def staticmethod_call(i: int) -> int:
            events.append(f"staticmethod_call:{i}")
            return i

        @classmethod
        @transaction
        def classmethod_call(cls, j: str) -> str:
            events.append(f"classmethod_call:{j}")
            return j

        @transaction
        def instancemethod_call(self, k: list | None = None) -> list | None:  # not supported
            return k

    @MyClass.staticmethod_call.rollback
    def rollback_staticmethod(i: int) -> bool:
        events.append(f"rollback_staticmethod:{i}")
        return True

    @MyClass.classmethod_call.rollback
    def rollback_classmethod(cls, j: str) -> bool:
        events.append(f"rollback_classmethod:{j}")
        return True

    with TransactionState(reraise=False):
        await step(1)
        MyClass.staticmethod_call(2)
        MyClass.classmethod_call("test string")
        raise_except("boom")

    assert events == [
        "step:1",
        "staticmethod_call:2",
        "classmethod_call:test string",
        "raise_except:boom",
        "undo_raise_exception:boom",
        "rollback_classmethod:test string",
        "rollback_staticmethod:2",
        "rollback_step:1",
    ]

    mc = MyClass()
    assert mc.instancemethod_call([1, 2, 3]) is None

    with pytest.raises(ValueError):
        transaction(lambda x: x + 1)
