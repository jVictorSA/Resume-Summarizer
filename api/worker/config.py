from core.config import env_config

from celery import Celery

user = env_config.RABBITMQ_DEFAULT_USER
password = env_config.RABBITMQ_DEFAULT_PASS
host = env_config.RABBITMQ_DEFAULT_HOST
port = env_config.RABBITMQ_DEFAULT_PORT

broker_url = f'amqp://{user}:{password}@{host}:{port}//'

app = Celery(
    'worker',
    broker=broker_url,
    backend='rpc://',
    include=['worker.summarize']
)

app.conf.update(
    result_expires=1800
)
