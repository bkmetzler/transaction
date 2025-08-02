import asyncio
import json
from contextvars import ContextVar
from contextvars import Token
from typing import ClassVar
from typing import Optional

from transaction.classes.function_call import FunctionCall


class TransactionState:
    """
    Class representation of keeping track of function calls and associated rollback calls, and the order
    in which they were called.
    """

    _current_state: ClassVar[ContextVar["TransactionState | None"]] = ContextVar(
        "current_transaction_state", default=None
    )

    def __init__(self, reraise: bool = True) -> None:
        """
        Initialize TransactionState to keep track of function calls

        Args:
            reraise: bool
                Should an exception be raised after rollback, if the exception is thrown while executing
                the initial functions.
        """
        self.stack: list[FunctionCall] = []
        self._token: Token[TransactionState | None] | None = None
        self._reraise = reraise

    def __begin(self) -> None:
        """
        Helper function to start collection of function calls.
        Used with Context Manager '__enter__', '__exit__', '__aenter__', and '__aexit__'

        Returns:
            None
        """
        self._token = self._current_state.set(self)

    def __end(self) -> None:
        """
        Helper function to end collection of function calls

        Returns:
            None
        """
        if self._token:
            self._current_state.reset(self._token)
            self._token = None

    def __enter__(self) -> "TransactionState":
        """
        Context Manager start
        Returns:
            TransactionState

        """
        self.__begin()
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object) -> bool:
        """
        Context Manager end
        Args:
            exc_type:
                If exception is thrown, this is the type of exception.
            exc_val:
                If exception is thrown, this is the value of exception.
            exc_tb:
                If exception is thrown, this it the traceback of exception.

        Returns:
            bool
                Should the exception be reraised or not
                True: Suppress exceptions
                False:  Reraise exception
        """
        if exc_type:
            asyncio.run(self.rollback())
        self.__end()
        return not self._reraise if exc_type else False

    async def __aenter__(self) -> "TransactionState":
        """
        Async Context Manager start

        Returns:
            TransactionState
        """
        self.__begin()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object
    ) -> bool:
        """
        Async Context Manager end
        Args:
            exc_type:
                If exception is thrown, this is the type of exception.
            exc_val:
                If exception is thrown, this is the value of exception.
            exc_tb:
                If exception is thrown, this it the traceback of exception.

        Returns:
            bool
                Should the exception be reraised or not
                True: Suppress exceptions
                False:  Reraise exception

        """
        if exc_type:
            await self.rollback()
        self.__end()
        return not self._reraise if exc_type else False

    def record_call(self, call: FunctionCall) -> None:
        """
        Record function call on Context stack

        Args:
            call: FunctionCall
                Definition of a function that has/will be called.

        Returns:
            None
        """
        self.stack.append(call)

    async def rollback(self) -> None:
        """
        Run all the 'rollback_func' functions and mark them as 'cls.rolled_back' to True.

        Returns:
            None
        """
        for call in reversed(self.stack):
            await call.rollback()
        self.stack.clear()

    def export_history(self) -> str:
        """
        Export stack history to string

        Returns: str
            JSON String representation of TransactionState and function call history
        """
        data = [call.to_dict() for call in self.stack]
        return json.dumps(data, indent=4)

    @classmethod
    def import_history(cls, json_str: str) -> "TransactionState":
        """
        Convert json_str back to a functioning TransactionState

        Args:
            json_str: str
                JSON String (created by cls.export_history)

        Returns:
            TransactionState
        """
        transaction_state = cls()
        transaction_state.stack.clear()
        transaction_state.stack.extend([FunctionCall.from_dict(item) for item in json.loads(json_str)])
        return transaction_state

    @classmethod
    def get_current(cls) -> Optional["TransactionState"]:
        """
        Get current Context State as TransactionState
        Returns:
            TransactionState | None

        """
        state = cls._current_state.get()
        if state is None:
            return None
        return state
