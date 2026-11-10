import uuid
from typing import Any

import pytest

from src.application.ports.message_broker import MessageBroker
from src.application.services.outbox_relay import OutboxRelay
from src.tracing import TRACE_HEADER, trace_scope
from tests.conftest import FakeMessageBroker, FakeUnitOfWork


class RaisingBroker(MessageBroker):
    async def send(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> None:
        raise RuntimeError("kafka unavailable")


@pytest.mark.asyncio
async def test_relay_sends_and_marks_published(
    fake_uow: FakeUnitOfWork, fake_broker: FakeMessageBroker
) -> None:
    await fake_uow.outbox.add("ad.created", {"ad_id": 1})
    await fake_uow.outbox.add("ad.updated", {"ad_id": 1})

    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=fake_broker)
    processed = await relay._process_batch()

    assert processed == 2
    assert fake_broker.sent == [
        {"event": "ad.created", "payload": {"ad_id": 1}},
        {"event": "ad.updated", "payload": {"ad_id": 1}},
    ]
    assert len(fake_broker.headers) == 2
    assert fake_uow.committed
    assert fake_uow.outbox.messages == []


@pytest.mark.asyncio
async def test_relay_noop_when_outbox_empty(
    fake_uow: FakeUnitOfWork, fake_broker: FakeMessageBroker
) -> None:
    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=fake_broker)
    processed = await relay._process_batch()

    assert processed == 0
    assert fake_broker.sent == []
    assert not fake_uow.committed


@pytest.mark.asyncio
async def test_relay_propagates_trace_id_from_outbox(
    fake_uow: FakeUnitOfWork, fake_broker: FakeMessageBroker
) -> None:
    with trace_scope("trace-1"):
        await fake_uow.outbox.add("ad.created", {"ad_id": 1})

    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=fake_broker)
    await relay._process_batch()

    assert fake_broker.headers == [{TRACE_HEADER: "trace-1"}]


@pytest.mark.asyncio
async def test_relay_generates_trace_id_when_outbox_has_none(
    fake_uow: FakeUnitOfWork, fake_broker: FakeMessageBroker
) -> None:
    await fake_uow.outbox.add("ad.created", {"ad_id": 1})

    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=fake_broker)
    await relay._process_batch()

    trace_id = fake_broker.headers[0][TRACE_HEADER]
    assert uuid.UUID(trace_id).version == 4


@pytest.mark.asyncio
async def test_relay_uses_separate_trace_id_per_message(
    fake_uow: FakeUnitOfWork, fake_broker: FakeMessageBroker
) -> None:
    with trace_scope("trace-1"):
        await fake_uow.outbox.add("ad.created", {"ad_id": 1})
    with trace_scope("trace-2"):
        await fake_uow.outbox.add("ad.updated", {"ad_id": 2})

    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=fake_broker)
    await relay._process_batch()

    assert [h[TRACE_HEADER] for h in fake_broker.headers] == ["trace-1", "trace-2"]


@pytest.mark.asyncio
async def test_relay_rolls_back_and_leaves_messages_on_broker_failure(
    fake_uow: FakeUnitOfWork,
) -> None:
    await fake_uow.outbox.add("ad.created", {"ad_id": 1})

    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=RaisingBroker())

    with pytest.raises(RuntimeError):
        await relay._process_batch()

    assert not fake_uow.committed
    assert fake_uow.rolled_back
    assert len(fake_uow.outbox.messages) == 1
