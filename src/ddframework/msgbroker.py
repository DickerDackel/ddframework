import queue

from collections import defaultdict
from typing import Any, Callable, Hashable, NamedTuple


MessageType = Hashable
MessageReceiver = Callable[Any, None]


class UnknownMessageType(BaseException): pass


class Message(NamedTuple):
    message: MessageType
    args: tuple[Any]
    kwargs: dict[str, Any]

    def __repr__(self):
        return f'{self.message}: {self.args}, {self.kwargs}'


class MessageBroker:
    def __init__(self) -> None:
        self._q = queue.SimpleQueue()
        self._receivers = defaultdict(set)

    def register(self,
                 callback: Callable[..., None],
                 *message_types: MessageType,
                 wants_command=False) -> None:
        for t in message_types:
            self._receivers[t].add((callback, wants_command))

    def reset(self):
        self._receivers.clear()

    def tick(self) -> None:
        while True:
            if self._q.empty():
                break

            try:
                msg = self._q.get_nowait()
            except queue.Empty:
                pass

            message, args, kwargs = msg

            if message not in self._receivers:
                raise UnknownMessageType(f'Message type {message} is not registered')

            for fn, wants_command in self._receivers[message]:
                if wants_command:
                    fn(message, *args, **kwargs)
                else:
                    fn(*args, **kwargs)

    def send(self, message: MessageType, *args: Any, **kwargs: Any) -> None:
        message = Message(message, args, kwargs)
        self._q.put(message)


broker = MessageBroker()
