import json

import structlog
from redis import Redis
logger = structlog.get_logger(__name__)


def write_event_to_redis(redis_client: Redis, queue: str, event: dict | tuple):
    logger.info(f"Write data to redis queue: {queue}, data: {event}")
    redis_client.rpush(queue, json.dumps(event))


def get_events_from_redis(redis_client: Redis, queue: str, batch_size: int):
    events = redis_client.lrange(queue, 0, batch_size -1)
    logger.info(f"Read data to redis queue: {queue}. Results: {events}")
    return [json.loads(event) for event in events]


def remove_events_from_redis(redis_client: Redis, queue: str, batch_size: int):
    logger.info(f"Remove data to redis queue: {queue}")
    redis_client.ltrim(queue, batch_size, -1)

