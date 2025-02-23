import os
import structlog
from celery import Task, Celery
from celery.schedules import crontab
from core.settings import CLICKHOUSE_INTERVAL_LOGS_PUSH

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('CELERY_CONFIG_MODULE', 'core.celeryconfig')

logger = structlog.get_logger(__name__)
app = Celery('events')
app.config_from_envvar('CELERY_CONFIG_MODULE')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'insert_events_to_click_house': {
        'task': 'insert_events_to_click_house',
        'schedule': crontab(f'*/{CLICKHOUSE_INTERVAL_LOGS_PUSH}', '*', '*', '*', '*')
    },
}
