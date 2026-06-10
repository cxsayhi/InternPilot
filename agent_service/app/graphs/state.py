from typing import Literal, TypedDict


class ApplicationAgentState(TypedDict, total=False):
    run_id: str
    user_id: str
    application_id: str
    resume_text: str
    job_text: str
    company: str | None
    role: str | None
    job_profile: dict
    resume_profile: dict
    match_result: dict
    rewrite_suggestions: list[dict]
    learning_plan: list[dict]
    warnings: list[str]
    errors: list[str]
    next_action: Literal[
        "extract_job",
        "extract_resume",
        "match",
        "rewrite",
        "plan",
        "done",
        "failed",
    ]

