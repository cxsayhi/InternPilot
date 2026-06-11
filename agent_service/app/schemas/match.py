from typing import Literal

from pydantic import BaseModel, Field


SkillMatchStatus = Literal["matched", "weak", "missing"]


class SkillEvidence(BaseModel):
    source: str = Field(min_length=1)
    text: str = Field(min_length=1)


class SkillMatch(BaseModel):
    skill: str = Field(min_length=1)
    status: SkillMatchStatus
    evidence: list[SkillEvidence] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class MatchResult(BaseModel):
    score: int = Field(ge=0, le=100)
    breakdown: dict[str, int] = Field(default_factory=dict)
    strongMatches: list[SkillMatch] = Field(default_factory=list)
    weakMatches: list[SkillMatch] = Field(default_factory=list)
    missingSkills: list[SkillMatch] = Field(default_factory=list)
