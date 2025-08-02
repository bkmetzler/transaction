# Current TODO list


- mypy errors
```bash
    $ nox -s mypy
    nox > Running session mypy
    nox > Creating virtual environment (virtualenv) using python3.12 in .nox/mypy
    nox > python -m pip install mypy
    nox > mypy -p transaction
    transaction/decorator.py: note: In member "__init__" of class "TransactionWrapper":
    transaction/decorator.py:28: error: Argument 1 to "__call__" of "_Wrapper" has incompatible type "TransactionWrapper"; expected "Callable[[VarArg(ParamSpec), KwArg(ParamSpecKwargs)], Awaitable[Never]]"  [arg-type]
    transaction/decorator.py:28: note: "TransactionWrapper.__call__" has type "Callable[[VarArg(ParamSpec), KwArg(ParamSpecKwargs)], T | Awaitable[T]]"
    transaction/decorator.py: note: In member "__call__" of class "TransactionWrapper":
    transaction/decorator.py:53: error: Incompatible return value type (got "T@__init__", expected "T@__call__ | Awaitable[T@__call__]")  [return-value]
    Found 2 errors in 1 file (checked 8 source files)
    nox > Command mypy -p transaction failed with exit code 1
    nox > Session mypy failed.
```
    - current workaround
        -- Add '# type: ignore' to appropriate error code
```python
    class TransactionWrapper:
        def __init__(self, func: Callable[P, T]) -> None:
            self.func = func
            self.rollback_func: Callable[..., Any] | None = None
            self._is_coroutine = inspect.iscoroutinefunction(func)
            wraps(func)(self)

        def rollback(self, func: Callable[..., Any]) -> Callable[..., Any]:
            self.rollback_func = func
            return func

        def __call__(self, *args: ParamSpec, **kwargs: ParamSpecKwargs) -> T | Awaitable[T]:
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
                    return await result  # type: ignore

                return wrapped()
            return result

```
