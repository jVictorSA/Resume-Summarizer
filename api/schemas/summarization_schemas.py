from pydantic import BaseModel, Field
from fastapi import UploadFile, Form
from typing import List, Optional
from uuid import uuid4

class SummaryInput(BaseModel):
    query: Optional[str] = Form(...)
    user_id: int = Form(...)

class SummaryModel(BaseModel):
    files: List[UploadFile]
    query: Optional[str]
    request_id: uuid4
    user_id: int

class Summary(BaseModel):
    summary: str
    strong_points: List[str]
    weak_points: List[str]
    score: float = Field(gt=0.0, le=10.0)

class CVAnalysis(BaseModel):
    cv_analysis: str =  Field(description="Detailed analysis of the given CV, based on the role description.")
    why_it_fits: str = Field(description="Detailed analysis and description of why this CV fits the role description.")
    things_to_watch_out: str = Field(description="Detailed analysis and description of points in this CV to keep an eye on based on the role description.")
    score: float = Field(gt=0.0, le=10.0, description="Score of how likely this CV fits the role description. Serves as CV ranking parameter.")

class SummaryAndAnalysis(BaseModel):
    cv_analysis: str =  Field(description="Detailed analysis of your thought process, what you've paid attention to given the role description, what you've been searching on the CVs given the role and what are the outcomes of your analysis, i.e. what are the most relevant candidates to the role.")
    summary: str = Field(description="Summary of the information on the given CV.")
    strong_points: List[str]
    weak_points: List[str]
    why_it_fits: str = Field(description="Detailed analysis and description of why this CV fits the role description.")
    things_to_watch_out: str
    ranking_score: float = Field(gt=0.0, le=10.0)


class CVsAnalysis(BaseModel):
    cvs_analysis: str =  Field(description="Detailed analysis of your thought process, what you've paid attention to given the role description, what you've been searching on the CVs given the role and what are the outcomes of your analysis, i.e. what are the most relevant candidates to the role.")
    summaries: List[CVAnalysis]

class CVsAnalysisResponse(BaseModel):
    cvs_analysis_process: str =  Field(description="Detailed analysis of your thought process, what you've paid attention to given the role description, what you've been searching on the CVs given the role and what are the outcomes of your analysis, i.e. what are the most relevant candidates to the role.")
    cvs_analysis: List[SummaryAndAnalysis]

class SummaryResponse(BaseModel):
    summaries: List[Summary]