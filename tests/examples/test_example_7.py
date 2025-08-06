from __future__ import annotations

import pytest

from transaction import transaction


def test_example_7() -> None:
    class MyClass:
        @staticmethod
        @transaction
        def static_method(i: int) -> int:
            return i

        @classmethod
        @transaction
        def class_method(cls, j: str) -> str:
            return j

    assert MyClass.static_method(5) == 5
    assert MyClass.class_method("hi") == "hi"

    def define_bad_class() -> None:
        class BadClass:
            """Simple container for testing decorator order."""

            @transaction
            @staticmethod
            def method(i: int) -> int:
                return i

        BadClass()  # pragma: no cover - instantiation for side effects

    with pytest.raises(ValueError):
        define_bad_class()
