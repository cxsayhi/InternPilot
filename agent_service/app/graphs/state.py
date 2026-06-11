from typing import TypedDict

from app.schemas.job import JobProfile
from app.schemas.match import MatchResult
from app.schemas.plan import LearningPlanItem
from app.schemas.resume import ResumeProfile
from app.schemas.rewrite import RewriteSuggestion
from app.schemas.run import AnalyzeApplicationResponse


class ApplicationAgentState(TypedDict, total=False):
    run_id: str
    user_id: str
    application_id: str
    resume_text: str
    job_text: str
    company: str | None
    role: str | None
    job_profile: JobProfile
    resume_profile: ResumeProfile
    match_result: MatchResult
    rewrite_suggestions: list[RewriteSuggestion]
    learning_plan: list[LearningPlanItem]
    response: AnalyzeApplicationResponse
    warnings: list[str]
    errors: list[str]
