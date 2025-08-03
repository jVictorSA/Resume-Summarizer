import re
import json
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException

from schemas.summarization_schemas import SummaryInput, Summary, CVsAnalysisResponse, SummaryResponse
from worker.summarize import summarize_cv

summaries_router = APIRouter()

@summaries_router.post("/summarize")
async def summarize_cvs(
    query: Optional[str] = Form(None),
    user_id: int = Form(...),
    files: List[UploadFile] = File(...)
) -> CVsAnalysisResponse | SummaryResponse:
    try: 
        print(f"{'='*80}\nRecebendo request\n{'='*80}")
        print(f"{'='*80}\nRole description:\n{query}\n\n{'='*80}")
        temp_file_storage = "/tmp/"
        pdf_filepaths = []
        image_filepaths = []
        payload = SummaryInput(query=query, user_id=user_id)

        print(f"{'='*80}\nCriando arquivos\n{'='*80}")
        for file in files:
            with open(f"{temp_file_storage}{file.filename}", "wb") as buffer:
                if  file.content_type != "application/pdf" \
                and file.content_type != "image/jpg" \
                and file.content_type != "image/jpeg" \
                and file.content_type != "image/png":
                    print(f"File type: {file.content_type} not supported.\n{file} will not be processed.")
                
                buffer.write(await file.read())
                if file.content_type == "application/pdf":
                    pdf_filepaths.append(f"{temp_file_storage}{file.filename}")
                elif file.content_type == "image/jpg" or file.content_type == "image/jpeg" or file.content_type == "image/png":
                    image_filepaths.append(f"{temp_file_storage}{file.filename}")

        cv_summaries_task = summarize_cv.delay(pdf_filepaths, image_filepaths, query)

        cv_summaries_result = cv_summaries_task.get(timeout=240)
        cv_summaries_result = re.sub(r'\\"', '', cv_summaries_result)
        cv_summaries_result = re.sub(r'\n', '', cv_summaries_result)
        cv_summaries_result = re.sub(r'\t', '', cv_summaries_result)
        print(f"{'='*80}\nArquivos sumarizados | Tipo: {type(cv_summaries_result)}\n{'='*80}")
        print(cv_summaries_result)

        if query is not None:
            cv_summaries_result: CVsAnalysisResponse = CVsAnalysisResponse(**json.loads(cv_summaries_result))
        else:
            cv_summaries_result: SummaryResponse = SummaryResponse(**json.loads(cv_summaries_result))


        return cv_summaries_result
    
        # return SummaryResponse(
        #     cvs_analysis="Ok",
        #     summaries=[
        #         Summary(
        #             summary='Summary',
        #             strong_points=["None"],
        #             weak_points=["None"],
        #             score=10.0
        #         )
        #     ]
        # )
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"There was an error during CV Summarization. Error message: {e}")