import importlib
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from typing import Self


@dataclass
class FunctionCall:
    name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    rollback_func: Callable[..., Any] | None = None
    rolled_back: bool = False
    exception: str | None = None

    def __str__(self) -> str:
        return f"{self.name}(args={self.args}, kwargs={self.kwargs})"

    async def rollback(self) -> None:
        if not self.rollback_func:
            self.exception = f"No rollback function for {self.name}"
            raise RuntimeError(self.exception)

        try:
            result = self.rollback_func(*self.args, **self.kwargs)
            if inspect.iscoroutine(result) or inspect.isawaitable(result):
                await result
            self.rolled_back = True
        except Exception as e:
            self.exception = f"{type(e).__name__}: {e}"
            raise

    def to_dict(self) -> dict[str, Any]:
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
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
        module_name, func_name = qualified_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func  # type: ignore[no-any-return]
