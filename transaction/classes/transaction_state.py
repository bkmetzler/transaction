import asyncio
import json
from contextvars import ContextVar
from contextvars import Token
from typing import ClassVar
from typing import Self

from transaction.classes.function_call import FunctionCall


class TransactionState:
    _current_state: ClassVar[ContextVar["TransactionState | None"]] = ContextVar(
        "current_transaction_state", default=None
    )

    def __init__(self, reraise: bool = True) -> None:
        self.stack: list[FunctionCall] = []
        self._token: Token[TransactionState | None] | None = None
        self._reraise = reraise

    def __begin(self) -> None:
        self._token = self._current_state.set(self)

    def __end(self) -> None:
        if self._token:
            self._current_state.reset(self._token)
            self._token = None

    def __enter__(self) -> "TransactionState":
        self.__begin()
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object) -> bool:
        if exc_type:
            asyncio.run(self.rollback())
        self.__end()
        return not self._reraise if exc_type else False

    async def __aenter__(self) -> "TransactionState":
        self.__begin()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object
    ) -> bool:
        if exc_type:
            await self.rollback()
        self.__end()
        return not self._reraise if exc_type else False

    def record_call(self, call: FunctionCall) -> None:
        self.stack.append(call)

    async def rollback(self) -> None:
        for call in reversed(self.stack):
            await call.rollback()
        self.stack.clear()

    def export_history(self) -> str:
        data = [call.to_dict() for call in self.stack]
        return json.dumps(data, indent=4)

    @classmethod
    def import_history(cls, json_str: str) -> Self:
        transaction_state = cls()
        transaction_state.stack.clear()
        transaction_state.stack.extend([FunctionCall.from_dict(item) for item in json.loads(json_str)])
        return transaction_state

    @classmethod
    def get_current(cls) -> "TransactionState | None":
        return cls._current_state.get()
