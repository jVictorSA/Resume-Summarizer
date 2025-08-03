from fastapi import FastAPI
from routes.cv_summarization_route import summaries_router
from routes.healthcheck_route import healthcheck_router

app = FastAPI(
    title="CV Summarizer API",
    summary="API for CV applications summarization & ranking of applicants",
    version="1.0.0"
)

app.include_router(summaries_router, prefix="/api", tags=["Summaries"])
app.include_router(healthcheck_router, prefix="/api", tags=["Healthcheck"])
