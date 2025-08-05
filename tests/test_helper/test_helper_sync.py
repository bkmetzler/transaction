from typing import Callable

import pytest
from pytest_lazyfixture import lazy_fixture
from contextlib import nullcontext
from contextlib import ContextDecorator

from tests.conftest import CustomException
from transaction.classes.transaction_state import TransactionState



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "context,func,vars1,vars2,expected",
    [
        (
                pytest.raises(
                    CustomException
                ),
                lazy_fixture("function_exception_example"),
                1,
                2,
                []
        ),
        # (nullcontext(), lazy_fixture("static_example"), []),
        # (nullcontext(), lazy_fixture("class_example"), []),
        # (nullcontext(), lazy_fixture("instance_example"), []),
        # (nullcontext(), lazy_fixture("function_exception_rollback_failed_example"), []),

    ],
)
async def test_sync_transaction_rollback(context: nullcontext | None, func: str, vars1: int, vars2: int, expected: list) -> None:
    called = []
    with context:
        with TransactionState(reraise=True):
            func(vars1)
            func(vars2)
    assert sorted(called) == sorted(expected)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "context,func,vars1,vars2,expected",
    [
        (nullcontext(), lazy_fixture("static_example"), 1, 1, []),
        # (nullcontext(), lazy_fixture("class_example"), 1, 1, []),
        # (nullcontext(), lazy_fixture("instance_example"), []),
        # (nullcontext(), lazy_fixture("function_exception_rollback_failed_example"), []),

    ],
)
async def test_sync_transaction_rollback(context: nullcontext | None, func: str, vars1: int, vars2: int, expected: list) -> None:
    called = []


    with context:
        with TransactionState():
            func.do(vars1)
            func.do(vars2)
    assert sorted(called) == sorted(expected)





#
#
#
# @pytest.mark.asyncio
# def test_sync_transaction_internal_exception_with_rollback(function_exception_example):
#     try:
#         func1_exception, func1_exception_rollback = function_exception_example
#         with TransactionState(reraise=True):
#             func1_exception(1)
#             func1_exception(2)
#             raise RuntimeError("fail")
#     except RuntimeError:
#         pass
#
#     assert called == ["do(1)", "do(2)", "undo(2)", "undo(1)"]
