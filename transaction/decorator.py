import inspect
from collections.abc import Awaitable
from collections.abc import Callable
from functools import wraps
from typing import Any
from typing import cast
from typing import ParamSpec
from typing import ParamSpecKwargs
from typing import TypeVar

from transaction.classes.function_call import FunctionCall
from transaction.classes.transaction_state import TransactionState


T = TypeVar("T")
P = ParamSpec("P")


def transaction(func: Callable[P, T] | staticmethod | classmethod) -> Callable[P, T | Awaitable[T]]:  # type: ignore[misc]
    """
    Decorator used to define initial functions
    Args:
        func:

    Returns:

    """
    if isinstance(func, (staticmethod, classmethod)):
        wrapped_func = TransactionWrapper(func.__func__)
        descriptor = type(func)(wrapped_func)
        setattr(descriptor, "rollback", wrapped_func.rollback)
        return cast(Callable[P, T | Awaitable[T]], descriptor)

    registrar = TransactionWrapper(func)
    return cast(Callable[P, T | Awaitable[T]], registrar)


class TransactionWrapper:
    """
    Class to help decorator with defining the rollback_func rollback function and if it is a coroutine or not
    """

    def __init__(self, func: Callable[P, T]) -> None:
        self.func = func
        self.rollback_func: Callable[..., Any] | None = None
        self._is_coroutine = inspect.iscoroutinefunction(func)
        wraps(func)(self)  # type: ignore[arg-type]

    def rollback(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Define rollback function for FunctionCall

        Args:
            func: Rollback function

        Returns:
            Inputted callable function
        """
        self.rollback_func = func
        return func

    def __call__(self, *args: ParamSpec, **kwargs: ParamSpecKwargs) -> T | Awaitable[T]:
        """
        Catch all calls not defined previously
        Record decorated function as a part of the TransactionState

        Args:
            *args: Arguments
            **kwargs: KeyWord Arguments

        Returns:
            Callable or Awaitable function

        """
        call = FunctionCall(
            name=self.func.__qualname__,
            args=args,
            kwargs=kwargs,
            rollback_func=self.rollback_func,
        )

        state = TransactionState.get_current()
        if state:
            state.record_call(call)

        # As we do not have access to the developers' code, we do not know paramspec or kwargspec.
        result = self.func(*args, **kwargs)  # type: ignore[arg-type]
        if self._is_coroutine and inspect.isawaitable(result):

            async def wrapped() -> T:
                return await result  # type: ignore[no-any-return]

            return wrapped()

        return result  # type: ignore[return-value]
