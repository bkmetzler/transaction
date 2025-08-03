import functools
import inspect
import types
from collections.abc import Callable
from enum import auto
from enum import Enum
from typing import Any


class FunctionType(Enum):
    REGULAR_FUNCTION = auto()
    INSTANCE_METHOD = auto()
    CLASS_METHOD = auto()
    STATIC_METHOD = auto()
    LAMBDA_FUNCTION = auto()
    BUILTIN_FUNCTION = auto()
    ASYNC_FUNCTION = auto()
    GENERATOR_FUNCTION = auto()
    COROUTINE_FUNCTION = auto()
    PARTIAL_FUNCTION = auto()
    UNKNOWN = auto()

    def is_callable(self) -> bool:
        if self in (
            FunctionType.ASYNC_FUNCTION,
            FunctionType.COROUTINE_FUNCTION,
            FunctionType.INSTANCE_METHOD,
            FunctionType.REGULAR_FUNCTION,
        ):
            return True
        return False

    def is_not_supported(self) -> bool:
        if self in (
            FunctionType.LAMBDA_FUNCTION,
            FunctionType.PARTIAL_FUNCTION,
            FunctionType.GENERATOR_FUNCTION,
            FunctionType.BUILTIN_FUNCTION,
        ):
            return False
        return True


def get_function_type(ctx: Any, func: Callable) -> FunctionType:  # type: ignore[type-arg]
    if isinstance(func, functools.partial):
        return FunctionType.PARTIAL_FUNCTION

    if isinstance(func, types.BuiltinFunctionType):
        return FunctionType.BUILTIN_FUNCTION

    if inspect.iscoroutinefunction(func):
        return FunctionType.ASYNC_FUNCTION

    if inspect.iscoroutine(func):
        return FunctionType.COROUTINE_FUNCTION

    if inspect.isgeneratorfunction(func):
        return FunctionType.GENERATOR_FUNCTION

    if inspect.ismethod(func):
        if func.__self__ is not None and isinstance(func.__self__, type):
            return FunctionType.CLASS_METHOD
        else:
            return FunctionType.INSTANCE_METHOD

    if inspect.isfunction(func):
        if func.__name__ == "<lambda>":
            return FunctionType.LAMBDA_FUNCTION
        elif func.__class__.__name__ == "function":
            return FunctionType.REGULAR_FUNCTION

        # Check for static/classmethod in class hierarchy
        for cls in inspect.getmro(ctx.__class__ if not isinstance(ctx, type) else ctx):
            if func.__name__ in cls.__dict__:
                attr = cls.__dict__[func.__name__]
                if isinstance(attr, staticmethod):
                    return FunctionType.STATIC_METHOD
                elif isinstance(attr, classmethod):
                    return FunctionType.CLASS_METHOD
        return FunctionType.REGULAR_FUNCTION

    return FunctionType.UNKNOWN


def inspect_function(func: Callable) -> FunctionType:  # type: ignore[type-arg]
    """
    Automatically determines the context and returns FunctionType.
    """
    ctx = getattr(func, "__self__", None) or func
    return get_function_type(ctx, func)


def get_class(func: Callable) -> Any:  # type:ignore[type-arg]
    if hasattr(func, "__class__"):
        return func.__class__
    return func
