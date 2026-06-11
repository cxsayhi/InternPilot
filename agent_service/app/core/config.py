from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    graph_version: str = "application_graph.v1"
    model_name: str = "deterministic-mvp-placeholder"
    job_extraction_mode: Literal["deterministic", "llm"] = "deterministic"
    job_extraction_model: str | None = None
    resume_extraction_mode: Literal["deterministic", "llm"] = "deterministic"
    resume_extraction_model: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        protected_namespaces=("settings_",),
    )


settings = Settings()
