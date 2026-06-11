from pydantic import BaseModel, Field


class LearningPlanItem(BaseModel):
    day: int = Field(ge=1, le=7)
    title: str = Field(min_length=1)
    tasks: list[str] = Field(min_length=1)
    targetSkills: list[str] = Field(default_factory=list)
    deliverable: str = Field(min_length=1)
