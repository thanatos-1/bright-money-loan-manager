import os

BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://')

CONTAINER_KILL_TIMEOUT = 4 * 60

CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
CELERY_IGNORE_RESULT = True

CELERY_IMPORTS = [
    "api.tasks"
]

CELERY_ROUTES = {
    "api.tasks.register_user" : {'queue':'register_user'}
}