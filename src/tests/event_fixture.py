import pytest
from faker import Faker

from core.base_model import Model
from core.event_log_client import EventModel
from users.use_cases import UserCreated


@pytest.fixture()
def get_event(
    faker: Faker,
    get_model_to_convert
) -> EventModel:
    return EventModel(
        event_type=faker.word(),
        event_date_time=faker.date_time(),
        environment=faker.word(),
        event_context=get_model_to_convert.model_dump_json()
    )


@pytest.fixture()
def get_model_to_convert(faker: Faker) -> Model:
    return UserCreated(
        email=faker.email(), first_name=faker.first_name(), last_name=faker.last_name()
    )


@pytest.fixture()
def write_event_to_redis(
    get_event: EventModel,
    queue_name,
    redis_client
) -> EventModel:
    redis_client.rpush(queue_name, get_event.model_dump_json())
    return get_event
