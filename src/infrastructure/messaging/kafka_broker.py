import json
import typing

from aiokafka import AIOKafkaProducer

from src.application.ports.message_broker import MessageBroker


class KafkaMessageBroker(MessageBroker):
    def __init__(self, producer: AIOKafkaProducer, topic: str) -> None:
        self._producer = producer
        self._topic = topic

    async def send(
        self,
        payload: dict[str, typing.Any],
        headers: dict[str, str],
    ) -> None:
        await self._producer.send_and_wait(
            self._topic,
            payload,
            headers=[(key, value.encode("utf-8")) for key, value in headers.items()],
        )


def serialize(value: dict[str, typing.Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False).encode("utf-8")
