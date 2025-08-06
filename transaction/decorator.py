import functools
import inspect
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import cast
from typing import ParamSpec
from typing import ParamSpecKwargs
from typing import TypeVar

from transaction.classes.function_call import FunctionCall
from transaction.classes.transaction_state import TransactionState
from transaction.helpers import FunctionType
from transaction.helpers import get_class
from transaction.helpers import inspect_function


T = TypeVar("T")
P = ParamSpec("P")


class StaticTransactionMethod(staticmethod):  # type: ignore[type-arg]
    def __init__(self, wrapped: Callable):  # type: ignore[type-arg]
        self._wrapper = TransactionWrapper(wrapped)
        super().__init__(self._wrapper)

    def rollback(self, rollback_func: Callable) -> Callable:  # type: ignore[type-arg]
        return self._wrapper.rollback(rollback_func)


class ClassTransactionMethod(classmethod):  # type: ignore[type-arg]
    def __init__(self, wrapped: Callable):  # type: ignore[type-arg]
        self._wrapper = TransactionWrapper(wrapped)
        super().__init__(self._wrapper)  # type: ignore[arg-type]

    def rollback(self, rollback_func: Callable) -> Callable:  # type: ignore[type-arg]
        return self._wrapper.rollback(rollback_func)


def transaction(func: Callable[P, T]) -> Callable[P, T | Awaitable[T]]:
    """
    Decorator used to define initial functions
    Args:
        func: callable/awaitable function

    Returns: callable/awaitable function
    """

    func_type = inspect_function(func)

    if not func_type.is_callable():
        if func_type == FunctionType.STATIC_METHOD:
            if isinstance(func, staticmethod):
                raise TypeError("@transaction must be applied before @staticmethod")
            return StaticTransactionMethod(func)
        elif func_type == FunctionType.CLASS_METHOD:
            if isinstance(func, classmethod):
                raise TypeError("@transaction must be applied before @classmethod")
            return ClassTransactionMethod(func)  # type: ignore[return-value]
        if not func_type.is_supported():
            raise ValueError(f"UNSUPPORTED TYPE: {func_type}")
        raise ValueError(f"UNKNOWN TYPE: {func_type}")

    # If standard function, then it falls down to here.
    wrapper = TransactionWrapper(func)
    return cast(Callable[P, T | Awaitable[T]], wrapper)


class TransactionWrapper:
    """
    Class to help decorator with defining the rollback_func rollback function and if it is a coroutine or not
    """

    def __init__(self, func: Callable[P, T]) -> None:
        self.func = func
        self.rollback_func: Callable[..., Any] | None = None
        self._is_coroutine = inspect.iscoroutinefunction(func)
        functools.update_wrapper(self, func)  # type: ignore[arg-type]

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
        func_type = inspect_function(self.func)

        if func_type == FunctionType.CLASS_METHOD:
            class_type = get_class(self.func)
            result = self.func(class_type, *args, **kwargs)  # type: ignore[arg-type]
        else:
            result = self.func(*args, **kwargs)  # type: ignore[arg-type]

        if self._is_coroutine and inspect.isawaitable(result):

            async def wrapped() -> T:
                return await result  # type: ignore[no-any-return]

            return wrapped()

        return result  # type: ignore[return-value]
