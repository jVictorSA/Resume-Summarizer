from typing import List
from pydantic import BaseModel
from instructor import from_gemini
from google.generativeai import configure, GenerativeModel
from google.generativeai.types import GenerationConfig

from core.config import env_config
from services.llm.retry import retry_strategy
from schemas.summarization_schemas import Summary, CVsAnalysis
from services.llm.prompts import CV_SUMMARY_PROMPT, CV_RANKING_PROMPT

class GeminiLLM():
    def __init__(self) -> None:
        configure(api_key=env_config.GEMINI_API_KEY)
        gemini_model = GenerativeModel(
            model_name=env_config.LLM_MODEL,
            generation_config=GenerationConfig(
                temperature=0.3,
                top_p=0.7,
            )
        )
        self.client = from_gemini(client=gemini_model)
        

    @retry_strategy
    def llm_interaction(self, system_prompt: str, user_prompt: str, response_schema: BaseModel):
        try:
            response = self.client.messages.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    },
                ],
                response_model=response_schema
                
            )

            return response
        
        except Exception as e:
            raise e
        

    def summarize_cv_texts(self, cv_text: str):
        try:
            print(f"{'='*80}\nSummarizando Currículo com LLM\n{'='*80}")
            return self.llm_interaction(
                system_prompt=CV_SUMMARY_PROMPT,
                user_prompt=f"Summarize the given CV text: \n\n\"{cv_text}\"",
                response_schema=Summary
            )
        
        except Exception as e:
            raise e

    def rank_cvs(self, role_description: str, cvs_text: List[str]):
        try:
            print(f"{'='*80}\nRankeando Currículo com LLM\n{'='*80}")
            return self.llm_interaction(
                system_prompt=CV_RANKING_PROMPT,
                user_prompt=f"Given the following \"Role description\" and \"CVs texts\", provide an analysis and rank them all: \n\n\"Role description\":\n{role_description}\n\n\"CVs texts\":\n\"{cvs_text}\"",
                response_schema=CVsAnalysis
            )
        
        except Exception as e:
            raise e