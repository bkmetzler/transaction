# Transaction

A lightweight Python 3.12+ library for tracking decorated function calls and supporting structured rollback logic.

## Features

- Sync + async support
- Rollback propagation (fail-fast)
- Per-task context isolation
- Export/import rollback state

## Usage

### Example 1
```python
    from transaction import TransactionState
    from transaction import transaction

    @transaction
    def step(i: int) -> int:
        return i

    @step.rollback
    def rollback_step(i: int) -> bool:
        ...

    @transaction
    def raise_except(j: str) -> str:
        raise Exception("Random Exception")

    @raise_except.rollback
    def undo_raise_exception(j: str) -> bool:
        return True

    with TransactionState(reraise=False) as state:
        step(1)
        step(2)
        step(3)
        raise_except("random string")
```

Explanation:
    After 'step' is ran 3 times, another function 'raise_except' is called, raising the exception.

    Once the exception is raised, TransactionState.rollback is automatically called. 'undo_raise_exception' is called, then
'rollback_step' is called the same 3 times, as 'rollback_step(3)', 'rollback_step(2)', and 'rollback_step(1)'.  Note the "rollback"
functions need to return a boolean.  If the rollback decoracted function returns boolean True, then it moves onto the next rollback function.

If the rollback decorated function returns False, it assumes that the rollback failed, and logs everything and exits.

You can control if the TransactionState re-raises the exception originally thrown, or if it is just consumed and lost forever.


### Example 2

```python
    from transaction import TransactionState
    from transaction import transaction

    @transaction
    def step_int(i: int) -> int:
        return i

    @step_int.rollback
    def rollback_step_int(i: int) -> bool:
        return True

    @transaction
    def step_str(j: str) -> str:
        return j

    @step_str.rollback
    def rollback_step_str(j: str) -> bool:
        return True

    with TransactionState():
        step_int(1)
        step_str("2")

```

Explanation:

As you might have noticed, the decorated function and its associated rollback function have the exact same arguments and keyword arguments.
The only difference between these definitions is the return type of boolean.  This boolean indicates if the rollback was successful or not.

| Return  | Result                                                                                                                                                                                  |
|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| True    | Rollback was successful.  Move onto next rollback step.                                                                                                                                 |
| False   | Rollback step failed.  Stop all execution and pass back to context manager.<br/>If context manager has flag "reraise=False", the exception that started the rollback will not be reraised. |


### Example 3
```python
    from transaction import TransactionState
    from transaction import transaction

    @transaction
    async def step(i: int) -> int:
        return i

    @step.rollback
    def rollback_step(i: int) -> bool:
        ...

    @transaction
    def raise_except(j: str) -> str:
        raise Exception("Random Exception")

    @raise_except.rollback
    async def undo_raise_exception(j: str) -> bool:
        return True

    with TransactionState(reraise=False) as state:
        # Yes, I know there should be an 'await' statement and it should be wrapped
        #  in an async function.  This is just a simple example showing what can be done.
        step(1)
        step(2)
        step(3)
        raise_except("random string")
```
Explanation:

As you can see here, the 'transaction' and 'rollback' decorators work on both sync and async functions.



### Example 4
```python
    from transaction import TransactionState
    from transaction import transaction

    @transaction
    async def step(i: int) -> int:
        return i

    @step.rollback
    def rollback_step(i: int) -> bool:
        ...

    @transaction
    def raise_except(j: str) -> str:
        raise Exception("Random Exception")

    @raise_except.rollback
    async def undo_raise_exception(j: str) -> bool:
        return True

    class MyClass:
        @staticmethod
        def staticmethod_call(i: int) -> int:
            return i

        @classmethod
        def classmethod_call(cls, j: str) -> str:
            return j

        @transaction
        def instancemethod_call(self, k: list | None = None) -> list | None:  # << Not Supported
            return k

        @instancemethod_call.rollback
        def instance_rollback(self, k: list | None = None) -> bool:  # << Not Supported
            return k


    with TransactionState(reraise=False) as state:
        # Next 3 lines are supported
        step(1)
        MyClass.staticmethod_call(2)
        MyClass.classmethod_call("test string")

        # This is not supported
        mc = MyClass()
        result = mc.instancemethod_call([1, 2, 3, 4])

        # The following is not supported
        func = lambda x: x + 1
        rollback_func = lambda x: x - 1
        transaction(func)
        func.rollback(rollback_func)


```

As you can see base functions, static methods and class methods all work properly.
An instance of a class and decorating lamdbdas do not work, and is not supported.



### Example 5

```python
    from transaction import TransactionState
    from transaction import transaction

    @transaction
    def step1(i: int) -> int:
        return i

    @step1.rollback
    def step1_rollback(i: int) -> bool:
        return True

    async with TransactionState() as state:
        step1(1)
        step1(2)
        step1(3)
```

Simple async context lock.


### Example 6

```python
    from transaction import TransactionState
    from transaction import transaction

    @transaction
    def step1(i: int) -> int:
        return i

    @step1.rollback
    def step1_rollback(i: int) -> bool:
        return True

    with TransactionState() as state:
        step1(1)
        step1(2)
        step1(3)
        export_json_str = state.export_history()
    # Save export_json_str to your favorite datastore, such as Redis, MSSQL, MySQL, etc.

    with TransactionState.import_history(export_json_str) as state:
        step1(4)
        step1(5)
        step1(6)
```

Export and import of transaction state.  Note the two sections indicate when it was exported and when it was imported.
At the end of this section, it would have logged 6 calls to "step1" with the different input variables.

### Example 7

```python
from transaction import transaction


class MyClass:
    @transaction
    @staticmethod
    def static_method(i: int) -> int:
        return i

    @transaction
    @classmethod
    def class_method(cls, j: str) -> str:
        return j
```

When stacking decorators, `@transaction` must wrap `@staticmethod` or `@classmethod` so the transaction wrapper sees the
final callable. Decorators are applied inside-out, so putting the descriptor decorators on top would hand `@transaction`
the descriptor object instead of the function. This library includes enhanced descriptor handling that lets the reversed
order work, but keeping `@transaction` outermost avoids relying on that behavior.
