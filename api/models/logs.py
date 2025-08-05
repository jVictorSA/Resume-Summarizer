import pymongo
from pydantic import Field
from typing import Optional
from datetime import datetime
from beanie import Document, Indexed

from schemas.summarization_schemas import SummaryResponse, CVsAnalysisResponse
from models.process_status_enum import ProcessStatusEnum

class CVsAnalysisLogs(Document):
    created_at: datetime
    updated_at: Optional[datetime] = None
    request_id: Indexed(str, unique=True)
    user_id: int
    timestamp: datetime
    query: Optional[str] = None
    result: Optional[SummaryResponse] | Optional[CVsAnalysisResponse] = None
    status: ProcessStatusEnum

    class Settings:
        indexes = [
            [("query", pymongo.TEXT)],
        ]