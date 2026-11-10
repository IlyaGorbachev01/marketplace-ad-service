import asyncio
import logging
from typing import Callable

from src.application.ports.message_broker import MessageBroker
from src.application.ports.uow import UnitOfWork
from src.tracing import TRACE_HEADER, trace_scope

logger = logging.getLogger(__name__)


class OutboxRelay:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        broker: MessageBroker,
        batch_size: int = 100,
        idle_sleep: float = 1.0,
    ) -> None:
        self._uow_factory = uow_factory
        self._broker = broker
        self._batch_size = batch_size
        self._idle_sleep = idle_sleep

    async def run(self) -> None:
        while True:
            try:
                published = await self._process_batch()
            except Exception:
                logger.exception("outbox relay batch failed")
                await asyncio.sleep(self._idle_sleep)
                continue
            if published == 0:
                await asyncio.sleep(self._idle_sleep)

    async def _process_batch(self) -> int:
        async with self._uow_factory() as uow:
            messages = await uow.outbox.fetch_unpublished(self._batch_size)
            if not messages:
                return 0

            for message in messages:
                with trace_scope(message.trace_id) as trace_id:
                    try:
                        await self._broker.send(
                            {
                                "event": message.event_type,
                                "payload": message.payload,
                            },
                            {TRACE_HEADER: trace_id},
                        )
                    except Exception:
                        logger.exception(
                            "failed to relay outbox message %s",
                            message.id,
                        )
                        raise
                    logger.info("relayed outbox message %s", message.id)

            await uow.outbox.mark_published([m.id for m in messages])
            await uow.commit()
            return len(messages)
