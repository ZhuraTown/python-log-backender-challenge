from django.db.models.signals import post_save
from django.dispatch import receiver

from core.event_log_client import EventLogClient
from core.redis_writer import write_event_to_redis
from core.settings import redis_client, EVENT_ACTIONS_QUEUE
from users.models import User
from users.use_cases import UserCreated


@receiver(post_save, sender=User)
def log_events(sender, instance: User, created, **kwargs):
    if created:
        events = EventLogClient.convert_data_to_model(
            [
                UserCreated(email=instance.email, first_name=instance.first_name, last_name=instance.last_name)
            ]
        )
        [write_event_to_redis(redis_client, EVENT_ACTIONS_QUEUE, event.model_dump(mode='json')) for event in events]
        return
