from pydantic import BaseModel, Field


class ApplicationAnalysisRequest(BaseModel):
    userId: str
    applicationId: str
    resumeText: str = Field(min_length=1)
    jobText: str = Field(min_length=1)
    company: str | None = None
    role: str | None = None


class RewriteSuggestion(BaseModel):
    originalBullet: str
    suggestedBullet: str
    targetedSkills: list[str] = Field(default_factory=list)
    evidenceSources: list[str] = Field(default_factory=list)
    unsupportedClaims: list[str] = Field(default_factory=list)
    confidence: float
    needsUserConfirmation: bool


class LearningPlanItem(BaseModel):
    day: int
    title: str
    tasks: list[str]
    targetSkills: list[str] = Field(default_factory=list)
    deliverable: str


class AgentMetadata(BaseModel):
    graphVersion: str
    model: str
    promptVersions: dict[str, str] = Field(default_factory=dict)


class ApplicationAnalysisResponse(BaseModel):
    runId: str
    matchScore: int
    scoreBreakdown: dict[str, int]
    strongMatches: list[dict] = Field(default_factory=list)
    weakMatches: list[dict] = Field(default_factory=list)
    missingSkills: list[dict] = Field(default_factory=list)
    rewriteSuggestions: list[RewriteSuggestion] = Field(default_factory=list)
    learningPlan: list[LearningPlanItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: AgentMetadata

