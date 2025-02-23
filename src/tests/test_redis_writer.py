import pytest

from core.redis_writer import write_event_to_redis, get_events_from_redis, remove_events_from_redis


class TestRedisWriter:

    @pytest.mark.parametrize(
        "event",
        [
            {"event_type": "test", "payload": {"data": 123}},
            ("test", 12312412412412, "TEST", {"data": 123})
        ]
    )
    def test_write_and_get_event(self, redis_client, queue_name, event, batch_size):
        write_event_to_redis(redis_client, queue_name, event)

        events = redis_client.lrange(queue_name, 0, batch_size)
        assert len(events) == 1

    def test_list_events(self, redis_client, queue_name, add_events_redis, batch_size):
        events = get_events_from_redis(redis_client, queue_name, batch_size)
        assert len(events) == 1
        assert events[0] == add_events_redis

    def test_remove_events(self, redis_client, queue_name, batch_size):
        event1 = {"event_type": "test", "payload": {"data": 123}}
        event2 = {"event_type": "test", "payload": {"data": 456}}
        write_event_to_redis(redis_client, queue_name, event1)
        write_event_to_redis(redis_client, queue_name,  event2)

        events = get_events_from_redis(redis_client, queue_name, batch_size=batch_size)
        assert len(events) == 2

        remove_events_from_redis(redis_client, queue_name, batch_size=batch_size)

        events_after = get_events_from_redis(redis_client, queue_name, batch_size=batch_size)
        assert len(events_after) == 0