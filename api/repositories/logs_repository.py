import logging
from typing import Optional, List

from models.logs import CVsAnalysisLogs
from schemas.log_schemas import CreateLogSchema, UpdateLogSchema, PublicLogSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogRepository: 
    @staticmethod
    async def create(http_request_id: str, log: CreateLogSchema) -> PublicLogSchema:
        try:
            logger.info(f"\n{'='*80}\nCREATING LOG DATA - LOG REPOSITORY CREATE\nrequest id: {http_request_id}\n{'='*80}")
            log_dict = log.model_dump()
            
            log_obj = CVsAnalysisLogs(**log_dict)
            await log_obj.insert()
            return log_obj

        except Exception as e:
            logger.critical(f"\n{'='*80}\nEXCEPTION - LOG CREATE\nrequest id: {http_request_id}\n{e}\n{'='*80}")
            raise e

    @staticmethod
    async def get_by_id(http_request_id: str, request_id: str) -> Optional[PublicLogSchema]:
        try:
            logger.info(f"\n{'='*80}\nRETRIEVING LOG DATA BY ID - LOG REPOSITORY GET BY ID\nrequest id: {http_request_id}\n{'='*80}")
            return await CVsAnalysisLogs.find_one(CVsAnalysisLogs.request_id == request_id)

        except Exception as e:
            logger.critical(f"\n{'='*80}\nEXCEPTION - LOG GET BY ID\nrequest id: {http_request_id}\n{e}\n{'='*80}")
            raise e

    
    @staticmethod
    async def get_all_paginated(
        http_request_id: str,
        skip: int = 0, 
        limit: int = 50
    ) -> List[PublicLogSchema]:
        try:
            logger.info(f"\n{'='*80}\nRETRIEVING LOG DATA PAGINATED - LOG REPOSITORY GET BY ID\nrequest id: {http_request_id}\n{'='*80}")
            return await CVsAnalysisLogs.find().skip(skip).limit(limit).to_list()

        except Exception as e:
            logger.critical(f"\n{'='*80}\nEXCEPTION - LOG GET PAGINATED\nrequest id: {http_request_id}\n{e}\n{'='*80}")
            raise e
    
    @staticmethod
    async def search(
        http_request_id: str,
        query: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[PublicLogSchema]:
        try:
            logger.info(f"\n{'='*80}\nTEXT SEARCHING LOG DATA - LOG REPOSITORY SEARCH\nrequest id: {http_request_id}\n{'='*80}")
            return await CVsAnalysisLogs.find(
                {
                    "$text": {"$search": query}
                }
            ).skip(skip).limit(limit).to_list()
        
        except Exception as e:
            logger.critical(f"\n{'='*80}\nEXCEPTION - LOG SEARCH\nrequest id: {http_request_id}\n{e}\n{'='*80}")
            raise e

    @staticmethod
    async def update(
        http_request_id: str,
        log: CVsAnalysisLogs, 
        log_update_data: UpdateLogSchema
    ) -> PublicLogSchema:
        try:
            logger.info(f"\n{'='*80}\nUPDATING LOG DATA - LOG REPOSITORY UPDATE\nrequest id: {http_request_id}\n{'='*80}")
            update_data = log_update_data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(log, field, value)
            
            await log.save()
            return log

        except Exception as e:
            logger.critical(f"\n{'='*80}\nEXCEPTION - LOG UPDATE\nrequest id: {http_request_id}\n{e}\n{'='*80}")
            raise e