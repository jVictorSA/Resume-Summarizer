from fastapi import APIRouter

healthcheck_router = APIRouter()

@healthcheck_router.get("/health")
def health_check():
    return {"status": "ok"}