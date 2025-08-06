import pytest

from transaction.decorator import ClassTransactionMethod
from transaction.decorator import StaticTransactionMethod
from transaction.decorator import transaction
from transaction.decorator import TransactionWrapper
from transaction.helpers import FunctionType


def test_transaction_staticmethod_wrong_order(monkeypatch: pytest.MonkeyPatch) -> None:
    sm = staticmethod(lambda: None)
    monkeypatch.setattr("transaction.decorator.inspect_function", lambda f: FunctionType.STATIC_METHOD)
    with pytest.raises(TypeError):
        transaction(sm)


def test_transaction_staticmethod_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    def func() -> None:
        pass

    monkeypatch.setattr("transaction.decorator.inspect_function", lambda f: FunctionType.STATIC_METHOD)
    wrapped = transaction(func)
    assert isinstance(wrapped, StaticTransactionMethod)

    @wrapped.rollback
    def rb() -> None:
        pass


def test_transaction_classmethod_wrong_order(monkeypatch: pytest.MonkeyPatch) -> None:
    cm = classmethod(lambda cls: None)
    monkeypatch.setattr("transaction.decorator.inspect_function", lambda f: FunctionType.CLASS_METHOD)
    with pytest.raises(TypeError):
        transaction(cm)


def test_transaction_classmethod_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    def func(cls) -> int:  # type: ignore[no-untyped-def]
        return 1

    monkeypatch.setattr("transaction.decorator.inspect_function", lambda f: FunctionType.CLASS_METHOD)
    wrapped = transaction(func)
    assert isinstance(wrapped, ClassTransactionMethod)

    @wrapped.rollback
    def rb(cls) -> None:  # type: ignore[no-untyped-def]
        pass


def test_transaction_unsupported_type(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("transaction.decorator.inspect_function", lambda f: FunctionType.LAMBDA_FUNCTION)
    with pytest.raises(ValueError, match="UNSUPPORTED TYPE"):
        transaction(lambda: None)


def test_transaction_unknown_type(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("transaction.decorator.inspect_function", lambda f: FunctionType.UNKNOWN)
    with pytest.raises(ValueError, match="UNKNOWN TYPE"):
        transaction(lambda: None)


def test_wrapper_class_method_call(monkeypatch: pytest.MonkeyPatch) -> None:
    class Dummy:
        called = None

    def cls_func(cls, val: int) -> int:
        Dummy.called = val
        return val

    wrapper = TransactionWrapper(cls_func)
    monkeypatch.setattr("transaction.decorator.inspect_function", lambda f: FunctionType.CLASS_METHOD)
    monkeypatch.setattr("transaction.decorator.get_class", lambda f: Dummy)
    assert wrapper(5) == 5
    assert Dummy.called == 5
