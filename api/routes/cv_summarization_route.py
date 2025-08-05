import logging
from datetime import datetime
from typing import List, Optional
from starlette.requests import Request
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends

from models.logs import CVsAnalysisLogs
from worker.summarize import summarize_cv
from schemas.log_schemas import CreateLogSchema, PublicLogSchema
from repositories.logs_repository import LogRepository
from models.process_status_enum import ProcessStatusEnum

summaries_router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@summaries_router.post("/summarize")
async def summarize_cvs(
    request: Request,
    query: Optional[str] = Form(None),
    user_id: int = Form(...),
    files: List[UploadFile] = File(...)
) -> PublicLogSchema:
    try: 
        log_repository: LogRepository = LogRepository()
        temp_file_storage = "/tmp/"
        pdf_filepaths = []
        image_filepaths = []
        request_id = request.state.request_id

        logger.info(f"\n{'='*80}\nRECEIVING REQUEST - SUMMARIZATION ROUTE SUMMARIZE_CVS\nrequest id: {request_id}\n{'='*80}")

        logger.info(f"\n{'='*80}\nCREATING FILES - SUMMARIZATION ROUTE SUMMARIZE_CVS\nrequest id: {request_id}\n{'='*80}")
        for file in files:
            with open(f"{temp_file_storage}{file.filename}", "wb") as buffer:
                if  file.content_type != "application/pdf" \
                and file.content_type != "image/jpg" \
                and file.content_type != "image/jpeg" \
                and file.content_type != "image/png":
                    logger.warning(f"\n{'='*80}\nFILE TYPE: {file.content_type} NOT SUPPORTED \n{file} WILL NOT BE PROCESSED \nSUMMARIZATION ROUTE SUMMARIZE_CVS\nrequest id: {request_id}\n{'='*80}")
                
                buffer.write(await file.read())
                if file.content_type == "application/pdf":
                    pdf_filepaths.append(f"{temp_file_storage}{file.filename}")
                elif file.content_type == "image/jpg" or file.content_type == "image/jpeg" or file.content_type == "image/png":
                    image_filepaths.append(f"{temp_file_storage}{file.filename}")


        logger.info(f"\n{'='*80}\nSAVING INITIAL LOG - SUMMARIZATION ROUTE SUMMARIZE_CVS\nrequest id: {request_id}\n{'='*80}")

        log: CreateLogSchema = CreateLogSchema(
            created_at=datetime.utcnow(),
            request_id = request_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            query=query,
            status=ProcessStatusEnum.PENDING
        )

        log_result: CVsAnalysisLogs = await log_repository.create(request_id, log)

        logger.info(f"\n{'='*80}\nSENDING TASK TO WORKER - SUMMARIZATION ROUTE SUMMARIZE_CVS\nrequest id: {request_id}\n{'='*80}")
        summarize_cv.delay(request_id, pdf_filepaths, image_filepaths, query)

        return log_result

    except Exception as e:
        logger.critical(f"\n{'='*80}\nEXCEPTION - SUMMARIZATION ROUTE SUMMARIZE_CVS\nrequest id: {request_id}\n{e}\n{'='*80}")
        raise HTTPException(status_code=500, detail=f"There was an error during CV Summarization. Error message: {e}")