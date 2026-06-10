from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    graph_version: str = "application_graph.v1"
    model_name: str = "deterministic-mvp-placeholder"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

