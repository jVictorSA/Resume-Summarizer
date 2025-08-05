import logging
from uuid import uuid4
from starlette.requests import Request
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from core.database import MongoDBManager
from routes.logs_route import logs_router
from routes.healthcheck_route import healthcheck_router
from routes.cv_summarization_route import summaries_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager = MongoDBManager.get_db_instance()

    await db_manager.connect()
    logger.info("MongoDB connected and initialized")
    
    yield 

    await db_manager.disconnect()
    logger.info("Application shutting down")

app = FastAPI(
    title="CV Summarizer API",
    summary="API for CV applications summarization & ranking of applicants",
    version="1.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

app.include_router(logs_router, prefix="/api", tags=["Logs"])
app.include_router(summaries_router, prefix="/api", tags=["Summaries"])
app.include_router(healthcheck_router, prefix="/api", tags=["Healthcheck"])