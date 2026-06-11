from pydantic import AliasChoices, BaseModel, ConfigDict, Field, computed_field


class RewriteSuggestion(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    originalBullet: str = Field(min_length=1)
    rewrittenBullet: str = Field(
        min_length=1,
        validation_alias=AliasChoices("rewrittenBullet", "suggestedBullet"),
    )
    targetedSkills: list[str] = Field(default_factory=list)
    evidenceSources: list[str] = Field(default_factory=list)
    unsupportedClaims: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    needsUserConfirmation: bool

    @computed_field
    @property
    def suggestedBullet(self) -> str:
        return self.rewrittenBullet
