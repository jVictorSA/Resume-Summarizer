import logging
from datetime import datetime
from typing import List, Optional
from starlette.requests import Request
from fastapi import APIRouter, HTTPException, status as http_status, Form

from core.database import MongoDBManager
from repositories.logs_repository import LogRepository
from models.process_status_enum import ProcessStatusEnum
from schemas.log_schemas import PublicLogSchema, CreateLogSchema
from schemas.summarization_schemas import SummaryResponse, CVsAnalysisResponse

logs_router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@logs_router.post("/logs")
async def create_log(
    request: Request,
    result: SummaryResponse | CVsAnalysisResponse,
    user_id: int,
    status: ProcessStatusEnum,
    query: Optional[str] = None
) -> PublicLogSchema:
    """
    Route for creating Summarization/Analysis log of CVs. 

    Input:

    - result: SummaryResponse | CVsAnalysisResponse - Result of CV Summarization or Analysis. See interative schema for type definition.
    - user_id: int -  User id.
    - status: ProcessStatusEnum - Enum concerning the status of log.
    - query: Optional[str] - User query stating what the user wants the LLM to analyze on the CVs.


    Return value if you pass SummaryResponse type on result:  
    {  
        "created_at": "YYYY-MM-DDTMM:MM:SS.mmZ",  
        "updated_at": None,  
        "request_id": "string",  
        "user_id": 0,  
        "timestamp": "YYYY-MM-DDTMM:MM:SS.mmZ",  
        "query": "string",  
        "result": {  
            "summaries": [  
                {  
                    "summary": "string",  
                    "strong_points": ["string"],  
                    "weak_points": ["string"],  
                    "score": 1  
                }  
            ]  
        },  
        "status": "PENDING"  
    }  
  
    Return value if you pass CVsAnalysisResponse type on result:  
    {  
        "created_at": "YYYY-MM-DDTMM:MM:SS.mmZ",  
        "updated_at": None,  
        "request_id": "string",  
        "user_id": 0,  
        "timestamp": "YYYY-MM-DDTMM:MM:SS.mmZ",  
        "query": "string",  
        "result": {  
            "cvs_analysis_process": "string",  
            "cvs_analysis": [  
                {  
                    "cv_analysis": "string"  
                    "summary": "string",  
                    "strong_points": ["string"],  
                    "weak_points": ["string"],  
                    "why_it_fits": ["string"],  
                    "things_to_watch_out": ["string"],  
                    "ranking_score": "string"  
                }  
            ]  
        },  
        "status": "PENDING"  
    }
    """

    try:
        request_id = request.state.request_id        
        logger.info(f"\n{'='*80}\nRECEIVING REQUEST - LOG ROUTE CREATE\nrequest id: {request_id}\n{'='*80}")
        
        logger.info(f"\n{'='*80}\nCHECKING THE PAYLOAD REQUEST_ID - LOG ROUTE CREATE\nrequest id: {request_id}\n{'='*80}")

        document = await LogRepository.get_by_id(request_id, request_id)
        
        if document is not None:
            raise HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail="An entry with this 'request_id' already exists.")

        logger.info(f"\n{'='*80}\nCREATING LOG DATA - LOG ROUTE CREATE\nrequest id: {request_id}\n{'='*80}")

        create_log_data: CreateLogSchema = CreateLogSchema(
            created_at=datetime.utcnow(),
            request_id=request_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            query=query,
            result=result,
            status=status
        ) 

        return await LogRepository.create(request_id, create_log_data)

    except HTTPException as http_exc:
        logger.critical(f"\n{'='*80}\nHTTP EXCEPTION - LOG ROUTE CREATE\nrequest id: {request_id}\n{http_exc}\n{'='*80}")
        raise http_exc

    except Exception as e:
        logger.critical(f"\n{'='*80}\nEXCEPTION - LOG ROUTE CREATE\nrequest id: {request_id}\n{e}\n{'='*80}")
        raise HTTPException(status_code=500, detail=f"There was an error during Log creation. Error message: {e}")

@logs_router.get("/logs/paginated")
async def get_all_logs_paginated(request: Request, skip: int = 0, limit: int = 10) -> List[PublicLogSchema]:
    """
    Route for retrieving CVs logs paginated by skip. 

    Input:

    - skip: int - Number of entries skipped before returning the page.
    - limit: int - Page limit of entries.
    

    Return value:  
    [  
        {  
            "created_at": "YYYY-MM-DDTMM:MM:SS.mmZ",  
            "updated_at": None,  
            "request_id": "string",  
            "user_id": 0,  
            "timestamp": "YYYY-MM-DDTMM:MM:SS.mmZ",  
            "query": "string",  
            "result": {  
                SummaryResponse | CVsAnalysisResponse
            },  
            "status": "PENDING"  
        }  
    ]
    """

    try:
        logger.info(f"\n{'='*80}\nRETRIEVING LOG DATA PAGINATED - LOG ROUTE GET ALL PAGINATED\nrequest id: {request.state.request_id}\n{'='*80}")
        return await LogRepository.get_all_paginated(request.state.request_id, skip, limit)
    except Exception as e:
        logger.critical(f"\n{'='*80}\nEXCEPTION - LOG ROUTE GET ALL PAGINATED\nrequest id: {request.state.request_id}\n{e}\n{'='*80}")
        raise HTTPException(status_code=500, detail=f"There was an error during Log paginated retrieval. Error message: {e}")

@logs_router.get("/logs/{request_id}")
async def get_log_by_id(request: Request, request_id: str) -> PublicLogSchema:
    """
    Route for retrieving log of CVs by request_id. 

    Input:

    - request_id: str - Request Id of the request that created the log.

    
    Return value:  
    {  
        "created_at": "YYYY-MM-DDTMM:MM:SS.mmZ",  
        "updated_at": None,  
        "request_id": "string",  
        "user_id": 0,  
        "timestamp": "YYYY-MM-DDTMM:MM:SS.mmZ",  
        "query": "string",  
        "result": {  
            SummaryResponse | CVsAnalysisResponse
        },  
        "status": "PENDING"  
    }  
    """

    try:
        logger.info(f"\n{'='*80}\nRETRIEVING LOG DATA BY ID - LOG ROUTE GET LOG BY ID\nrequest id: {request.state.request_id}\n{'='*80}")
        return await LogRepository.get_by_id(request.state.request_id, request_id)
    except Exception as e:
        logger.critical(f"\n{'='*80}\nEXCEPTION - LOG ROUTE GET LOG BY ID\nrequest id: {request.state.request_id}\n{e}\n{'='*80}")
        raise HTTPException(status_code=500, detail=f"There was an error during Log retrieval by id. Error message: {e}")

@logs_router.post("/logs/search/")
async def search_entries(request: Request, query: str) -> List[PublicLogSchema]:
    """
    Route for retrieving CVs logs based on query attribute search. 

    Input:

    - query: str - Search string that will be searched on the query attribute on the database log entries.
    

    Return value:  
    [  
        {  
            "created_at": "YYYY-MM-DDTMM:MM:SS.mmZ",  
            "updated_at": None,  
            "request_id": "string",  
            "user_id": 0,  
            "timestamp": "YYYY-MM-DDTMM:MM:SS.mmZ",  
            "query": "string",  
            "result": {  
                SummaryResponse | CVsAnalysisResponse
            },  
            "status": "PENDING"  
}  
    ]
    """

    try:
        logger.info(f"\n{'='*80}\nTEXT SEARCHING LOG DATA - LOG ROUTE SEARCH ENTRIES\nrequest id: {request.state.request_id}\n{'='*80}")
        return await LogRepository.search(request.state.request_id, query)
    except Exception as e:
        logger.critical(f"\n{'='*80}\nEXCEPTION - LOG ROUTE SEARCH ENTRIES\nrequest id: {request.state.request_id}\n{e}\n{'='*80}")
        raise HTTPException(status_code=500, detail=f"There was an error during Log text search. Error message: {e}")