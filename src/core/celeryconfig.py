from core.settings import CELERY_BROKER

broker_url = CELERY_BROKER
result_backend = CELERY_BROKER
broker_heartbeat = 10
broker_pool_limit = 100

task_default_queue = "default"
task_serializer = 'json'
accept_content = ['application/json']
result_serializer = 'json'
timezone = 'Europe/Moscow'
enable_utc = True


worker_pool_restarts = True
worker_send_task_events = True


imports = ['tasks.click_house_task']
