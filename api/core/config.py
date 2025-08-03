import os
from dotenv import load_dotenv

from schemas.config_schema import ConfigClass

load_dotenv()

env_config = ConfigClass(
    GEMINI_API_KEY=os.getenv('GEMINI_API_KEY'),
    LLM_MODEL=os.getenv('LLM_MODEL'),
    RABBITMQ_DEFAULT_USER=os.getenv('RABBITMQ_DEFAULT_USER'),
    RABBITMQ_DEFAULT_PASS=os.getenv('RABBITMQ_DEFAULT_PASS'),
    RABBITMQ_DEFAULT_HOST=os.getenv('RABBITMQ_DEFAULT_HOST'),
    RABBITMQ_DEFAULT_PORT=os.getenv('RABBITMQ_DEFAULT_PORT')
)