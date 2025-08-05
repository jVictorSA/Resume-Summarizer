from core.config import env_config
from core.database import MongoDBManager

import logging
from celery import Celery

user = env_config.RABBITMQ_DEFAULT_USER
password = env_config.RABBITMQ_DEFAULT_PASS
host = env_config.RABBITMQ_DEFAULT_HOST
port = env_config.RABBITMQ_DEFAULT_PORT

broker_url = f'amqp://{user}:{password}@{host}:{port}//'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Celery(
    'worker',
    broker=broker_url,
    backend='rpc://',
    include=['worker.summarize']
)

@app.on_after_configure.connect
def setup_db_connection(sender, **kwargs):
    try:
        MongoDBManager.initialize_db()
    except Exception as e:
        logger.critical(f"\n{'='*80}\nEXCEPTION\nFAILED TO INITIALIZE DATABASE IN CELERY WORKER\nWORKER CONFIG\n\n{e}\n{'='*80}")
        raise SystemExit(1) from e

@app.on_after_finalize.disconnect
def shutdown_db_connection(sender, **kwargs):
    MongoDBManager.close_db()

app.conf.update(
    result_expires=1800
)
