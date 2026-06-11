from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ProjectEvidence(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    project_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("project_id", "projectId"),
    )
    name: str | None = None
    description: str | None = None
    tech_stack: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("tech_stack", "techStack"),
    )
    evidence_text: str = Field(
        min_length=1,
        validation_alias=AliasChoices("evidence_text", "evidenceText"),
    )
    source: str = Field(default="pasted_resume_text", min_length=1)

    @property
    def projectId(self) -> str | None:
        return self.project_id

    @property
    def techStack(self) -> list[str]:
        return self.tech_stack

    @property
    def evidenceText(self) -> str:
        return self.evidence_text
