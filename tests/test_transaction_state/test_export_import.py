import json

from transaction.classes.function_call import FunctionCall
from transaction.classes.transaction_state import TransactionState
from transaction.decorator import transaction


# Dummy function
@transaction
def dummy_func(x: int) -> int:
    return x


# Dummy rollback function
@dummy_func.rollback
def rollback_func(x: int) -> bool:
    return True


def test_export_import_roundtrip():
    call1 = FunctionCall(name="func1", args=(1,), kwargs={}, rolled_back=True)
    call2 = FunctionCall(name="func2", args=(2,), kwargs={"a": "b"}, rolled_back=False, exception="Boom!")

    raw_data = json.dumps([call1.to_dict(), call2.to_dict()])
    txn = TransactionState.import_history(raw_data)

    tmp_history = txn.export_history()
    with TransactionState.import_history(tmp_history) as state:
        assert len(state.stack) == 2
        assert state.stack[0].name == "func1"
        assert state.stack[1].exception == "Boom!"


def test_export_import_history():
    with TransactionState() as state:
        state.record_call(
            FunctionCall(
                name="dummy_func", args=(1,), kwargs={}, rollback_func=rollback_func, rolled_back=False, exception=None
            )
        )
        state.record_call(
            FunctionCall(
                name="dummy_func", args=(2,), kwargs={}, rollback_func=rollback_func, rolled_back=False, exception=None
            )
        )
        json_data = state.export_history()
        j_data = json.loads(json_data)
        assert j_data == [
            {
                "name": "dummy_func",
                "args": [1],
                "kwargs": {},
                "rollback_func": "test_export_import.rollback_func",
                "rolled_back": False,
                "exception": None,
            },
            {
                "name": "dummy_func",
                "args": [2],
                "kwargs": {},
                "rollback_func": "test_export_import.rollback_func",
                "rolled_back": False,
                "exception": None,
            },
        ]
        assert isinstance(json_data, str)
        assert '"name": "dummy_func"' in json_data
        assert '"rollback_func": "test_export_import.rollback_func"' in json_data

        state.rollback()
        json_data = state.export_history()
    assert isinstance(json_data, str)
    assert '"name": "dummy_func"' in json_data
    assert '"rollback_func": "test_export_import.rollback_func"' in json_data

    with TransactionState.import_history(json_data) as txn:
        assert len(txn.stack) == 2
        for call in txn.stack:
            assert call.name == "dummy_func"
            assert call.rolled_back is False
            assert call.to_dict()["rollback_func"] == "test_export_import.rollback_func"
