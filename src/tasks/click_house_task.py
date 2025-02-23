import structlog
from celery import shared_task

from core.event_log_client import EventModel, EventLogClient
from core.redis_writer import get_events_from_redis, remove_events_from_redis
from core.settings import CLICKHOUSE_BATCH_SIZE, EVENT_ACTIONS_QUEUE, redis_client

logger = structlog.get_logger()


@shared_task(name="insert_events_to_click_house")
def insert_events_to_click_house():
    logger.info(f"Start task insert_events_to_click_house")
    logger.info(f"BATCH_SIZE: {CLICKHOUSE_BATCH_SIZE} EVENT_ACTIONS_QUEUE: {EVENT_ACTIONS_QUEUE}")
    new_raw_events = get_events_from_redis(redis_client, EVENT_ACTIONS_QUEUE, CLICKHOUSE_BATCH_SIZE)

    logger.info(f"Found new events: {len(new_raw_events)}")
    if not new_raw_events: return

    logger.info(f"Insert new events")
    with EventLogClient.init() as client:
        client.insert(
            data=[EventModel(**e) for e in new_raw_events]
        )

    logger.info(f"Remove new events")
    remove_events_from_redis(redis_client, EVENT_ACTIONS_QUEUE, CLICKHOUSE_BATCH_SIZE)
