import uuid

import pytest
from aio_pika import Connection, connect

from mirumon.application.devices.events.device_base_event import DeviceBaseEvent
from mirumon.infra.devices.devices_broker_repo_impl import DevicesBrokerRepoImpl

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
async def broker_repo(default_settings) -> DevicesBrokerRepoImpl:
    dsn = str(default_settings.rabbit_dsn)
    connection: Connection = await connect(dsn)
    return DevicesBrokerRepoImpl(connection=connection, process_timeout=2)


async def test_broker_repo_consume_published_event(broker_repo: DevicesBrokerRepoImpl):
    event = DeviceBaseEvent(
        sync_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="test_consume_passed",
        event_attributes={},
    )

    await broker_repo.publish_event(event)

    published_event = await broker_repo.consume(event.device_id, event.sync_id)
    assert published_event == {
        "device_id": str(event.device_id),
        "event_attributes": {},
        "event_type": "test_consume_passed",
        "sync_id": str(event.sync_id),
    }


async def test_broker_repo_consume_three_published_events(
    broker_repo: DevicesBrokerRepoImpl,
):
    event1 = DeviceBaseEvent(
        sync_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="event1",
        event_attributes={},
    )
    event2 = DeviceBaseEvent(
        sync_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="event2",
        event_attributes={},
    )
    event3 = DeviceBaseEvent(
        sync_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="event3",
        event_attributes={},
    )

    await broker_repo.publish_event(event1)
    await broker_repo.publish_event(event2)
    await broker_repo.publish_event(event3)

    published_event1 = await broker_repo.consume(event1.device_id, event1.sync_id)
    published_event2 = await broker_repo.consume(event2.device_id, event2.sync_id)
    published_event3 = await broker_repo.consume(event3.device_id, event3.sync_id)

    assert published_event1 == {
        "device_id": str(event1.device_id),
        "event_attributes": {},
        "event_type": "event1",
        "sync_id": str(event1.sync_id),
    }
    assert published_event2 == {
        "device_id": str(event2.device_id),
        "event_attributes": {},
        "event_type": "event2",
        "sync_id": str(event2.sync_id),
    }
    assert published_event3 == {
        "device_id": str(event3.device_id),
        "event_attributes": {},
        "event_type": "event3",
        "sync_id": str(event3.sync_id),
    }


async def test_broker_repo_consume_published_event_with_given_params_only(
    broker_repo: DevicesBrokerRepoImpl,
):
    device_id = uuid.uuid4()
    sync_id = uuid.uuid4()
    event = DeviceBaseEvent(
        sync_id=sync_id,
        device_id=device_id,
        event_type="test_consume_with_params_passed",
        event_attributes={},
    )
    skip_event_with_same_device = DeviceBaseEvent(
        sync_id=uuid.uuid4(),
        device_id=device_id,
        event_type="skip_consume",
        event_attributes={},
    )
    skip_event_with_same_sync_id = DeviceBaseEvent(
        sync_id=sync_id,
        device_id=uuid.uuid4(),
        event_type="skip_consume",
        event_attributes={},
    )
    skip_event = DeviceBaseEvent(
        sync_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        event_type="skip_consume",
        event_attributes={},
    )
    await broker_repo.publish_event(skip_event_with_same_sync_id)
    await broker_repo.publish_event(skip_event_with_same_device)
    await broker_repo.publish_event(skip_event)

    await broker_repo.publish_event(event)

    published_event = await broker_repo.consume(
        event.device_id, event.sync_id, timeout_in_sec=10
    )
    assert published_event == {
        "device_id": str(device_id),
        "event_attributes": {},
        "event_type": "test_consume_with_params_passed",
        "sync_id": str(sync_id),
    }
