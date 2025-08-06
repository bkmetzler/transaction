import importlib
import inspect
import json
import pickle
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from typing import cast
from typing import Union

from transaction.helpers import FunctionType
from transaction.helpers import get_class
from transaction.helpers import inspect_function


@dataclass
class FunctionCall:
    """
    Class to represent a function call and its associated rollback function
    """

    name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    rollback_func: Callable[..., Any] | None = None  # noqa
    rolled_back: bool = False
    exception: str | None = None

    def __str__(self) -> str:
        """
        Return string representation of class instance

        Returns: str
        """
        return f"{self.name}(args={self.args}, kwargs={self.kwargs})"

    async def rollback(self) -> None:
        """
        Execute 'self.rollback_func' and mark 'self.rolled_back' to True.
        'self.rollback_func' is a custom function to rollback the current function.

        Returns:
            None

        """
        if not self.rollback_func:
            self.exception = f"No rollback function for {self.name}"
            raise RuntimeError(self.exception)

        try:
            func_type = inspect_function(self.rollback_func)
            if func_type == FunctionType.CLASS_METHOD:
                class_type = get_class(self.rollback_func)
                result = self.rollback_func(class_type, *self.args, **self.kwargs)
            else:
                result = self.rollback_func(*self.args, **self.kwargs)

            if inspect.iscoroutine(result) or inspect.isawaitable(result):
                await result
            self.rolled_back = True
        except Exception as e:
            self.exception = f"{type(e).__name__}: {e}"
            raise
        self.rolled_back = True

    def to_dict(self) -> dict[str, Any]:
        """
        Returns dict version of data in 'self'

        Returns:
            dict[str, Any]
                dict representation of FunctionCall
        """
        return {
            "name": self.name,
            "args": self.args,
            "kwargs": self.kwargs,
            "rollback_func": (
                f"{self.rollback_func.__module__}.{self.rollback_func.__name__}" if self.rollback_func else None
            ),
            "rolled_back": self.rolled_back,
            "exception": self.exception,
        }

    def to_json(self) -> str:
        """
        Returns string version returned by 'to_dict()'

        Returns:
            str
                JSON string representation of FunctionCall
        """
        return json.dumps(self.to_dict(), indent=4)

    def to_pickle(self) -> bytes:
        """
        Matching helper function for "cls.from_pickle".

        Returns:
            bytes
                Pickled instance version of FunctionCall
        """

        return pickle.dumps(self)

    @classmethod
    def from_pickle(cls, pickle_bytes: bytes) -> Union["FunctionCall", Any]:
        """
        This is more of a helper function to convert a pickled instance of class.
        Good use with Redis

        Args:
            pickle_bytes:
                Pickled version of FunctionCall
        Returns:
            FunctionCall
        """
        return cast(FunctionCall, pickle.loads(pickle_bytes))

    @classmethod
    def from_json(cls, in_json: str) -> "FunctionCall":
        """
        Convert from JSON string to an instance of the class

        Args:
            cls:
                ClassMethod definition
            in_json: str
                Representation of JSON data needed for 'cls.from_dict()'

        Returns:
            FunctionCall
        """
        return cls.from_dict(json.loads(in_json))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FunctionCall":
        """
        Convert from dict to FunctionCall.

        Used to read from an external data source.

        Args:
            data: dict
                Representation of FunctionCall.
        Returns:
            FunctionCall

        """
        rollback_func = cls._resolve_function(data["rollback_func"]) if data["rollback_func"] else None
        return cls(
            name=data["name"],
            args=tuple(data["args"]),
            kwargs=dict(data["kwargs"]),
            rollback_func=rollback_func,
            rolled_back=data.get("rolled_back", False),
            exception=data.get("exception"),
        )

    @staticmethod
    def _resolve_function(qualified_name: str) -> Callable[..., Any]:
        """
        Convert qualified_name dot notation to a callable function/classmethod/staticmethod to use
        with Python's internal __import__() function.

        Args:
            qualified_name: str
                dot notation string of a function to be imported
        Returns:

        """
        module_name, func_name = qualified_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func  # type: ignore[no-any-return]
