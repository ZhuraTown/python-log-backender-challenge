import uuid
from collections.abc import Generator
from unittest.mock import ANY

import pytest
from clickhouse_connect.driver import Client
from django.conf import settings
from redis import Redis

from core.redis_writer import get_events_from_redis
from users.use_cases import CreateUser, CreateUserRequest, UserCreated

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def f_use_case() -> CreateUser:
    return CreateUser()


def test_user_created(f_use_case: CreateUser) -> None:
    request = CreateUserRequest(
        email='test@email.com', first_name='Test', last_name='Testovich',
    )

    response = f_use_case.execute(request)

    assert response.result.email == 'test@email.com'
    assert response.error == ''


def test_emails_are_unique(f_use_case: CreateUser) -> None:
    request = CreateUserRequest(
        email='test@email.com', first_name='Test', last_name='Testovich',
    )

    f_use_case.execute(request)
    response = f_use_case.execute(request)

    assert response.result is None
    assert response.error == 'User with this email already exists'


def test_event_log_entry_published(
    f_use_case: CreateUser,
    redis_client: Redis,
    queue_name: str,
    batch_size,
) -> None:
    email = f'test_{uuid.uuid4()}@email.com'
    request = CreateUserRequest(
        email=email, first_name='Test', last_name='Testovich',
    )

    f_use_case.execute(request)

    redis_data = get_events_from_redis(redis_client, queue_name, batch_size)

    assert redis_data[0] == {
        "event_type": "user_created",
        "event_date_time": ANY,
        "environment": "Local",
        "event_context": UserCreated(email=email, first_name='Test', last_name='Testovich').model_dump_json()
    }
