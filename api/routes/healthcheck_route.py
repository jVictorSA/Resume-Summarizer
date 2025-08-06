from fastapi import APIRouter

healthcheck_router = APIRouter()

@healthcheck_router.get("/health")
def health_check():
    """
    Route for checking if the API is online. 
    """
    return {"status": "ok"}