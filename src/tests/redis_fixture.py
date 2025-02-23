import json

import pytest

from core.settings import EVENT_ACTIONS_QUEUE


@pytest.fixture()
def add_events_redis(redis_client, queue_name: str):
    event = {"event_type": "test", "payload": {"data": 123}}
    redis_client.rpush(queue_name, json.dumps(event))
    return event


@pytest.fixture(scope='session')
def queue_name():
    return EVENT_ACTIONS_QUEUE


@pytest.fixture(scope='session')
def batch_size():
    return 100
