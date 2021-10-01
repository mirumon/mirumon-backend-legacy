import uuid

import pytest
from aio_pika import Connection, connect

from mirumon.application.devices.events.device_event import DeviceEvent
from mirumon.infra.devices.devices_broker_repo_impl import DevicesBrokerRepoImpl

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
async def broker_repo(default_settings) -> DevicesBrokerRepoImpl:
    dsn = str(default_settings.rabbit_dsn)
    connection: Connection = await connect(dsn)
    repo = DevicesBrokerRepoImpl(connection=connection, process_timeout=2)
    await repo.start()
    return repo


async def test_broker_repo_consume_published_event(broker_repo: DevicesBrokerRepoImpl):
    event = DeviceEvent(
        event_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="test_consume_passed",
        event_attributes={},
        correlation_id=uuid.uuid4(),
    )

    await broker_repo.publish_event(event)

    published_event = await broker_repo.get(event.device_id, event.correlation_id)
    assert published_event == {
        "device_id": str(event.device_id),
        "event_attributes": {},
        "event_type": "test_consume_passed",
        "event_id": str(event.event_id),
        "correlation_id": str(event.correlation_id),
    }


async def test_broker_repo_consume_three_published_events(
    broker_repo: DevicesBrokerRepoImpl,
):
    event1 = DeviceEvent(
        event_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="event1",
        event_attributes={},
        correlation_id=uuid.uuid4(),
    )
    event2 = DeviceEvent(
        event_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="event2",
        event_attributes={},
        correlation_id=uuid.uuid4(),
    )
    event3 = DeviceEvent(
        event_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="event3",
        event_attributes={},
        correlation_id=uuid.uuid4(),
    )

    await broker_repo.publish_event(event1)
    await broker_repo.publish_event(event2)
    await broker_repo.publish_event(event3)

    published_event1 = await broker_repo.get(event1.device_id, event1.correlation_id)
    published_event2 = await broker_repo.get(event2.device_id, event2.correlation_id)
    published_event3 = await broker_repo.get(event3.device_id, event3.correlation_id)

    assert published_event1 == {
        "device_id": str(event1.device_id),
        "event_attributes": {},
        "event_type": "event1",
        "event_id": str(event1.event_id),
        "correlation_id": str(event1.correlation_id),
    }
    assert published_event2 == {
        "device_id": str(event2.device_id),
        "event_attributes": {},
        "event_type": "event2",
        "event_id": str(event2.event_id),
        "correlation_id": str(event2.correlation_id),
    }
    assert published_event3 == {
        "device_id": str(event3.device_id),
        "event_attributes": {},
        "event_type": "event3",
        "event_id": str(event3.event_id),
        "correlation_id": str(event3.correlation_id),
    }


async def test_broker_repo_consume_published_event_with_given_params_only(
    broker_repo: DevicesBrokerRepoImpl,
):
    event = DeviceEvent(
        event_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        correlation_id=uuid.uuid4(),
        event_type="test_consume_with_params_passed",
        event_attributes={},
    )
    skip_event_with_same_device = DeviceEvent(
        event_id=uuid.uuid4(),
        device_id=event.device_id,
        event_type="skip",
        event_attributes={},
        correlation_id=uuid.uuid4(),
    )
    skip_event_with_same_correlation_id = DeviceEvent(
        event_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="skip",
        correlation_id=event.correlation_id,
        event_attributes={},
    )
    skip_event = DeviceEvent(
        event_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="skip",
        event_attributes={},
        correlation_id=None,
    )
    await broker_repo.publish_event(skip_event_with_same_correlation_id)
    await broker_repo.publish_event(skip_event_with_same_device)
    await broker_repo.publish_event(skip_event)

    await broker_repo.publish_event(event)

    published_event = await broker_repo.get(
        event.device_id, event.correlation_id, timeout_in_sec=10
    )
    assert published_event == {
        "event_id": str(event.event_id),
        "event_type": "test_consume_with_params_passed",
        "event_attributes": {},
        "device_id": str(event.device_id),
        "correlation_id": str(event.correlation_id),
    }
