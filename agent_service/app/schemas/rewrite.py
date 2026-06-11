from pydantic import BaseModel, Field


class RewriteSuggestion(BaseModel):
    originalBullet: str = Field(min_length=1)
    suggestedBullet: str = Field(min_length=1)
    targetedSkills: list[str] = Field(default_factory=list)
    evidenceSources: list[str] = Field(default_factory=list)
    unsupportedClaims: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    needsUserConfirmation: bool
