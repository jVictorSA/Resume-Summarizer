from pydantic import BaseModel

class ConfigClass(BaseModel):
    LLM_MODEL: str
    GEMINI_API_KEY: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_DEFAULT_HOST: str
    RABBITMQ_DEFAULT_PORT: str
    MONGODB_URL: str
    MONGODB_DB_NAME: str