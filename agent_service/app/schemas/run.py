from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.match import SkillMatch
from app.schemas.plan import LearningPlanItem
from app.schemas.rewrite import RewriteSuggestion


LLM_OUTPUT_VALIDATION_FAILED = "LLM_OUTPUT_VALIDATION_FAILED"
AgentErrorCode = Literal[
    "LLM_OUTPUT_VALIDATION_FAILED",
    "INVALID_REQUEST",
    "INTERNAL_ERROR",
]


class AgentError(BaseModel):
    code: AgentErrorCode
    message: str = Field(min_length=1)
    retryable: bool = False
    runId: str | None = None


class AgentMetadata(BaseModel):
    graphVersion: str
    model: str
    promptVersions: dict[str, str] = Field(default_factory=dict)


class AnalyzeApplicationRequest(BaseModel):
    userId: str
    applicationId: str
    resumeText: str = Field(min_length=1)
    jobText: str = Field(min_length=1)
    company: str | None = None
    role: str | None = None


class AnalyzeApplicationResponse(BaseModel):
    runId: str
    matchScore: int = Field(ge=0, le=100)
    scoreBreakdown: dict[str, int]
    strongMatches: list[SkillMatch] = Field(default_factory=list)
    weakMatches: list[SkillMatch] = Field(default_factory=list)
    missingSkills: list[SkillMatch] = Field(default_factory=list)
    rewriteSuggestions: list[RewriteSuggestion] = Field(default_factory=list)
    learningPlan: list[LearningPlanItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: AgentMetadata


ApplicationAnalysisRequest = AnalyzeApplicationRequest
ApplicationAnalysisResponse = AnalyzeApplicationResponse
