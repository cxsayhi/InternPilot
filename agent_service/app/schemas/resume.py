from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.schemas.project import ProjectEvidence


class ResumeProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    education: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectEvidence] = Field(default_factory=list)
    work_experience: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("work_experience", "workExperience", "experiences"),
    )
    evidence_bullets: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("evidence_bullets", "evidenceBullets", "bullets"),
    )
    weak_points: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("weak_points", "weakPoints"),
    )
    skill_evidence: dict[str, list[str]] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("skill_evidence", "skillEvidence"),
    )

    @property
    def bullets(self) -> list[str]:
        return self.evidence_bullets

    @property
    def experiences(self) -> list[str]:
        return self.work_experience

    @property
    def weakPoints(self) -> list[str]:
        return self.weak_points

    @property
    def skillEvidence(self) -> dict[str, list[str]]:
        return self.skill_evidence
