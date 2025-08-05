from worker.config import app
from core.database import MongoDBManager
from services.llm.llm_summarizer import GeminiLLM
from repositories.logs_repository import LogRepository
from models.logs import CVsAnalysisLogs
from models.process_status_enum import ProcessStatusEnum
from schemas.log_schemas import UpdateLogSchema
from schemas.summarization_schemas import Summary, CVsAnalysis, SummaryResponse, CVsAnalysisResponse, SummaryAndAnalysis

import re
import os
import time
import asyncio
import logging
import pytesseract
from PIL import Image
from pypdf import PdfReader
from datetime import datetime
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_pdf_text(request_id:str, file: str) -> str | None:
    logger.info(f"\n{'='*80}\nEXTRACTING PDFS TEXT - WORKER EXTRACT_PDF_TEXT\nrequest id: {request_id}\n{'='*80}")
    try:
        reader = PdfReader(file)

        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            page_text = re.sub(r'\n', ' ', page_text)
            page_text = re.sub(r'\s+', ' ', page_text)
            pages_text.append(page_text)
    
        extracted_text = '\n\n'.join(pages_text)

        return extracted_text
    except Exception as e:
        logger.critical(f"\n{'='*80}\nEXCEPTION - WORKER EXTRACT_PDF_TEXT\nrequest id: {request_id}{e}\n{'='*80}")
        raise e

def extract_image_text(request_id:str, filepaths: List[str]):
    logger.info(f"\n{'='*80}\nEXTRACTING IMAGES TEXT - WORKER EXTRACT_IMAGE_TEXT\nrequest id: {request_id}\n{'='*80}")
    try:
        images_text = []
        for image in filepaths:
            pytesseract_config = '--oem 3 -l por+eng'
            image = Image.open(image)
            image_text = pytesseract.image_to_string(image, config=pytesseract_config)

            images_text.append(image_text)
    
        extracted_text = '\n\n'.join(images_text)

        return extracted_text

    except Exception as e:
        logger.critical(f"\n{'='*80}\nEXCEPTION - WORKER EXTRACT_IMAGE_TEXT\nrequest id: {request_id}\n{e}\n{'='*80}")
        raise e

def group_image_cvs(request_id: str, images_files: List[str]) -> dict:
    logger.info(f"\n{'='*80}\nGROUPING IMAGES - WORKER GROUP_IMAGE_CVS\nrequest id: {request_id}\n{'='*80}")
    same_cv_images = {}

    for filepath in images_files:
        image_filename = filepath[5:25]

        if image_filename in same_cv_images:
            same_cv_images[image_filename].append(filepath)
        else:
            same_cv_images[image_filename] = []
            same_cv_images[image_filename].append(filepath)
    
    return same_cv_images

@app.task
def summarize_cv(
    request_id: str,
    pdf_files: List[str],
    image_files: List[str],
    query: Optional[str] = None
) -> None:
    start_time = time.monotonic()
    try:
        logger.info(f"\n{'='*80}\nINITIALIZING WORKER TASK - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")
        log_repository: LogRepository = LogRepository()
        gemini_service = GeminiLLM()
        loop = asyncio.get_event_loop()
        log_entry = loop.run_until_complete(log_repository.get_by_id(request_id, request_id))

        logger.info(f"\n{'='*80}\nGROUPING SIMILAR IMAGE FILES - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")
        
        cvs_texts = []
        cvs_summaries = []
        cvs_analysis = []

        same_cv_images = group_image_cvs(request_id, image_files)

        logger.info(f"\n{'='*80}\nEXTRACTING PDF TEXTS - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")
        for filepath in pdf_files:
            cvs_texts.append(extract_pdf_text(request_id, filepath))

        logger.info(f"\n{'='*80}\nEXTRACTING IMAGE TEXTS - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")
        for filepaths in same_cv_images.values():
            cvs_texts.append(extract_image_text(request_id, filepaths))
            
        logger.info(f"\n{'='*80}\nSUMMARIZING CVS - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")
        for cv in cvs_texts:
            cv_summary: Summary = gemini_service.summarize_cv_texts(request_id, cv)
            cvs_summaries.append(cv_summary)
        
        if query != "":
            logger.info(f"\n{'='*80}\nRANKING CVS - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")
            cvs_ranking: CVsAnalysis = gemini_service.rank_cvs(request_id, query, cvs_summaries)


            logger.info(f"\n{'='*80}\nGROUPING SUMMARIES AND RANKING DATA ON CVS ANALYSIS DATA TYPE - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")
            for summary_item, cv_analysis_item in zip(cvs_summaries, cvs_ranking.summaries):
                combined_item = SummaryAndAnalysis(
                    summary=summary_item.summary,
                    strong_points=summary_item.strong_points,
                    weak_points=summary_item.weak_points,
                    
                    
                    cv_analysis=cv_analysis_item.cv_analysis,
                    why_it_fits=cv_analysis_item.why_it_fits,
                    things_to_watch_out=cv_analysis_item.things_to_watch_out,
                    ranking_score=cv_analysis_item.score
                )
                cvs_analysis.append(combined_item)

            cvs_ranking_response: CVsAnalysisResponse =  CVsAnalysisResponse(
                cvs_analysis_process=cvs_ranking.cvs_analysis,
                cvs_analysis=cvs_analysis
            )


            logger.info(f"\n{'='*80}\nSORTING CVS ANALYSIS BY SCORE - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")
            cvs_ranking_response.cvs_analysis.sort(
                key=lambda cv_analysis: cv_analysis.ranking_score,
                reverse=True
            )

            logger.info(f"\n{'='*80}\nUPDATING CVS ANALYSIS LOG - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")

            log_update_data: UpdateLogSchema = UpdateLogSchema(
                updated_at=datetime.utcnow(),
                result=cvs_ranking_response,
                status=ProcessStatusEnum.SUCCESS
            )

            loop.run_until_complete(log_repository.update(request_id, log_entry, log_update_data))
        
        else:
            logger.info(f"\n{'='*80}\nORGANIZING AND SORTING CVS SUMMARIES BY SCORE - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")
            summaries: SummaryResponse = SummaryResponse(summaries=cvs_summaries)
            summaries.summaries.sort(
                key=lambda cv_summary: cv_summary.score,
                reverse=True
            )
            
            logger.info(f"\n{'='*80}\nUPDATING CVS SUMMARIES LOG - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")

            log_update_data: UpdateLogSchema = UpdateLogSchema(
                updated_at=datetime.utcnow(),
                result=summaries,
                status=ProcessStatusEnum.SUCCESS
            )

            loop.run_until_complete(log_repository.update(request_id, log_entry, log_update_data))
    
    except Exception as e:
        logger.critical(f"\n{'='*80}\nEXCEPTION - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{e}\n{'='*80}")
        
        log_entry = loop.run_until_complete(log_repository.get_by_id(request_id, request_id))
        log_update_data: UpdateLogSchema = UpdateLogSchema(
            result=None,
            status=ProcessStatusEnum.FAILED
        )

        loop.run_until_complete(log_repository.update(request_id, log_entry, log_update_data))

        raise e

    finally:
        for filepath in pdf_files:
            if os.path.exists(filepath):
                os.remove(filepath)

        for filepath in image_files:
            if os.path.exists(filepath):
                os.remove(filepath)

        logger.info(f"\n{'='*80}\nPROCESSED CVS IN {time.monotonic()-start_time:.2f}s - WORKER SUMMARIZE_CV\nrequest id: {request_id}\n{'='*80}")