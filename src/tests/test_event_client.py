from clickhouse_connect.driver import Client
from unittest.mock import ANY

from redis import Redis

from core.event_log_client import EventModel, EventLogClient
from core.redis_writer import get_events_from_redis, remove_events_from_redis
from users.use_cases import UserCreated


class TestEventClient:

    def test_correct_convert_model(
        self,
        get_model_to_convert: UserCreated
    ):
        converted_models = EventLogClient.convert_data_to_model([get_model_to_convert])
        assert converted_models
        assert isinstance(converted_models[0], EventModel)
        assert converted_models[0].event_context == get_model_to_convert.model_dump_json()

    def test_insert_event_to_click_house(
        self,
        get_event: EventModel,
        f_ch_client: Client,
    ):
        with EventLogClient.init() as client:
            client.insert(data=[get_event])

        log = f_ch_client.query(f"SELECT * FROM default.event_log WHERE event_type = '{get_event.event_type}'")
        assert log.result_rows == [
            (
                get_event.event_type,
                ANY,
                get_event.environment,
                get_event.event_context,
                1,
            ),
        ]

    def test_cast_write_events_from_redis_to_click_house(
        self,
        f_ch_client: Client,
        write_event_to_redis: EventModel,
        redis_client: Redis,
        queue_name,
        batch_size,
    ):
        new_raw_events = get_events_from_redis(redis_client, queue_name, batch_size)
        events = [EventModel(**e) for e in new_raw_events]

        with EventLogClient.init() as client:
            client.insert(data=events)

        log = f_ch_client.query(f"SELECT * FROM default.event_log WHERE event_type = '{write_event_to_redis.event_type}'")
        assert log.result_rows == [
            (
                write_event_to_redis.event_type,
                ANY,
                write_event_to_redis.environment,
                write_event_to_redis.event_context,
                1,
            ),
        ]

        remove_events_from_redis(redis_client, queue_name, batch_size)

        assert len(redis_client.lrange(queue_name, 0, batch_size -1)) == 0
