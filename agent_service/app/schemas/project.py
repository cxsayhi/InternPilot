from pydantic import BaseModel, Field


class ProjectEvidence(BaseModel):
    projectId: str | None = None
    name: str | None = None
    description: str | None = None
    techStack: list[str] = Field(default_factory=list)
    evidenceText: str = Field(min_length=1)
    source: str = Field(default="pasted_resume_text", min_length=1)
