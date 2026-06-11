from pydantic import BaseModel, Field

from app.schemas.project import ProjectEvidence


class ResumeProfile(BaseModel):
    skills: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)
    projects: list[ProjectEvidence] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experiences: list[str] = Field(default_factory=list)
