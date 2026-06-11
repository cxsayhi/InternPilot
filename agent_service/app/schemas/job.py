from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


SkillImportance = Literal["required", "preferred", "bonus"]


class ExtractedSkill(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1)
    category: str | None = None
    importance: SkillImportance = "required"
    evidence_text: str | None = Field(
        default=None,
        validation_alias=AliasChoices("evidence_text", "evidenceText"),
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @property
    def evidenceText(self) -> str | None:
        return self.evidence_text


class JobProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role_title: str | None = Field(
        default=None,
        validation_alias=AliasChoices("role_title", "roleTitle", "role"),
    )
    company: str | None = None
    required_skills: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("required_skills", "requiredSkills"),
    )
    preferred_skills: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("preferred_skills", "preferredSkills"),
    )
    responsibilities: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    seniority: str | None = None
    extracted_skills: list[ExtractedSkill] = Field(
        default_factory=list,
        validation_alias=AliasChoices("extracted_skills", "extractedSkills"),
    )

    @property
    def role(self) -> str | None:
        return self.role_title

    @property
    def requiredSkills(self) -> list[str]:
        return self.required_skills

    @property
    def preferredSkills(self) -> list[str]:
        return self.preferred_skills

    @property
    def extractedSkills(self) -> list[ExtractedSkill]:
        return self.extracted_skills
