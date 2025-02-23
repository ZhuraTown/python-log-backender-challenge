from typing import Generator

import clickhouse_connect
import pytest
from clickhouse_connect.driver import Client

from core import settings
from core.settings import CLICKHOUSE_HOST, redis_client as redis

pytest_plugins = [
    "tests.redis_fixture",
    "tests.event_fixture",
]


def create_event_log_table(client: Client):
    client.query(
        """
        CREATE TABLE IF NOT EXISTS event_log
        (
            `event_type` String,
            `event_date_time` DateTime64(6),
            `environment` String,
            `event_context` String,
            `metadata_version` Int32 DEFAULT 1,
        )
        ENGINE = MergeTree()
        PARTITION BY toYYYYMM(event_date_time)
        ORDER BY (event_date_time, event_type)
        SETTINGS index_granularity = 8192
        """
    )


@pytest.fixture(scope='module')
def f_ch_client() -> Client:
    client = clickhouse_connect.get_client(host=CLICKHOUSE_HOST)
    create_event_log_table(client)
    yield client
    client.close()


@pytest.fixture()
def redis_client():
    redis.flushall()
    yield redis


@pytest.fixture(autouse=True)
def f_clean_up_event_log(f_ch_client: Client) -> Generator:
    f_ch_client.query(f'TRUNCATE TABLE {settings.CLICKHOUSE_EVENT_LOG_TABLE_NAME}')
    yield
