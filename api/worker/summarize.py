from worker.config import app
from schemas.summarization_schemas import Summary, CVsAnalysis, SummaryResponse, CVsAnalysisResponse, SummaryAndAnalysis
from services.llm.llm_summarizer import GeminiLLM

import re
import os
import time
import pytesseract
from PIL import Image
from io import BytesIO
from pypdf import PdfReader
from typing import Optional, List
from fastapi import UploadFile, File

def extract_pdf_text(file: str) -> str | None:
    print(f"{'='*80}\nExtraindo documento: {file}\n{'='*80}")
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
        print(f"{'='*80}\nEXCEPTION - extract_pdf_text\n{e}\n{'='*80}")
        raise e

def extract_image_text(filepaths: List[str]):
    print(f"{'='*80}\nExtraindo texto de imagens\n{'='*80}")
    try:
        images_text = []
        for image in filepaths:
            print(f"{'='*80}\nExtraindo texto de imagem: {image}\n{'='*80}")
            pytesseract_config = '--oem 3 -l por+eng'
            image = Image.open(image)
            image_text = pytesseract.image_to_string(image, config=pytesseract_config)

            images_text.append(image_text)
    
        extracted_text = '\n\n'.join(images_text)

        return extracted_text

    except Exception as e:
        print(f"{'='*80}\nEXCEPTION - extract_image_text\n{e}\n{'='*80}")
        raise e

def group_image_cvs(images_files: List[str]) -> dict:
    same_cv_images = {}

    print(f"{'='*80}\nSeparando imagens\n{'='*80}")
    for filepath in images_files:
        image_filename = filepath[5:25]
        print(f"{'='*80}\nFilepaths: {filepath} - {image_filename}\n{'='*80}")

        if image_filename in same_cv_images:
            same_cv_images[image_filename].append(filepath)
        else:
            same_cv_images[image_filename] = []
            same_cv_images[image_filename].append(filepath)
    
    return same_cv_images

@app.task
def summarize_cv(pdf_files: List[str], image_files: List[str], query: Optional[str] = None) -> dict:
    start_time = time.monotonic()
    try:
        gemini_service = GeminiLLM()

        print(f"{'='*80}\nSumarizando documentos\n{'='*80}")
        print(f"{'='*80}\nRole description:\n{query}\n\n{'='*80}")
        cvs_texts = []
        cvs_summaries = []
        cvs_analysis = []

        same_cv_images = group_image_cvs(image_files)

        print(f"{'='*80}\nExtraindo textos de pdfs\n{'='*80}")
        for filepath in pdf_files:
            cvs_texts.append(extract_pdf_text(filepath))

        print(f"{'='*80}\nExtraindo textos de imagens\n{'='*80}")
        for filepaths in same_cv_images.values():
            print(f"{'='*80}\n same_cv_images Filepaths: {filepaths}\n{'='*80}")
            cvs_texts.append(extract_image_text(filepaths))
            
        print(f"{'='*80}\nTextos extraídos\nSummarizando currículos:\n")
        for cv in cvs_texts:
            cv_summary: Summary = gemini_service.summarize_cv_texts(cv)
            cvs_summaries.append(cv_summary)
            print(f"{'='*80}\n{cv_summary}\n{'='*80}")
        print(f"\n{'='*80}")
        
        if query is not None:
            print(f"{'='*80}\nRankeando CVs\n{'='*80}")
            cvs_ranking: CVsAnalysis = gemini_service.rank_cvs(query, cvs_summaries)

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

            cvs_ranking_response.cvs_analysis.sort(
                key=lambda cv_analysis: cv_analysis.ranking_score,
                reverse=True,

            )

            return cvs_ranking_response.model_dump_json()

        return SummaryResponse(summaries=cvs_summaries).model_dump_json()
    
    except Exception as e:
        print(f"{'='*80}\nEXCEPTION - summarize_cv\n{e}\n{'='*80}")
        raise e

    finally:
        for filepath in pdf_files:
            if os.path.exists(filepath):
                os.remove(filepath)

        for filepath in image_files:
            if os.path.exists(filepath):
                os.remove(filepath)

        print(f"Processed {len(cvs_texts)} CVs in {time.monotonic()-start_time:.2f}s")