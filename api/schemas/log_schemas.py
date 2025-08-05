from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from models.process_status_enum import ProcessStatusEnum
from schemas.summarization_schemas import SummaryResponse, CVsAnalysisResponse

class CreateLogSchema(BaseModel):
    created_at: datetime
    request_id: str
    user_id: int
    timestamp: datetime
    query: Optional[str] = None
    result: Optional[SummaryResponse] | Optional[CVsAnalysisResponse] = None
    status: ProcessStatusEnum

class UpdateLogSchema(BaseModel):
    updated_at: datetime = datetime.utcnow()
    result: Optional[SummaryResponse] | Optional[CVsAnalysisResponse] = None
    status: ProcessStatusEnum

class PublicLogSchema(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime]
    request_id: str
    user_id: int
    timestamp: datetime
    query: Optional[str] = None
    result: Optional[SummaryResponse] | Optional[CVsAnalysisResponse] = None
    status: ProcessStatusEnum