from __future__ import annotations

import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.schemas.resume import ResumeProfile
from app.services.structured_output import validate_structured_output


RESUME_EXTRACTION_PROMPT_VERSION = "langchain_resume_extraction.v1"
RESUME_EXTRACTION_REPAIR_PROMPT_VERSION = "langchain_resume_extraction_repair.v1"

RESUME_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You extract student resumes into a strict ResumeProfile. Preserve "
            "original evidence text whenever possible. Do not invent education, "
            "skills, projects, work experience, outcomes, dates, or weak points.",
        ),
        (
            "human",
            "Extract this resume.\n\n"
            "Required output fields:\n"
            "- education: education entries copied or tightly summarized from text\n"
            "- skills: normalized skill names explicitly supported by the resume\n"
            "- skill_evidence: map each skill to supporting original text snippets\n"
            "- projects: project evidence objects with name, description, tech_stack, "
            "evidence_text, and source\n"
            "- work_experience: work/internship experience entries with original evidence\n"
            "- evidence_bullets: strongest original resume bullets or lines\n"
            "- weak_points: missing/unclear areas visible from the resume only\n\n"
            "Resume text:\n{resume_text}",
        ),
    ]
)

RESUME_EXTRACTION_REPAIR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Repair a failed structured ResumeProfile extraction. Preserve source "
            "evidence from the original resume and return a valid ResumeProfile.",
        ),
        (
            "human",
            "Original resume:\n{resume_text}\n\n"
            "Invalid output:\n{invalid_output}\n\n"
            "Pydantic validation errors:\n{validation_errors}\n\n"
            "Return a corrected ResumeProfile.",
        ),
    ]
)


def extract_resume_profile_from_text(
    resume_text: str,
    llm: Any | None = None,
) -> ResumeProfile:
    model = llm or create_resume_extraction_llm()
    raw_output = build_resume_extraction_chain(model).invoke(
        {"resume_text": resume_text}
    )

    return validate_structured_output(
        ResumeProfile,
        raw_output,
        repair_fn=lambda payload, error: repair_resume_profile_output(
            resume_text=resume_text,
            invalid_output=payload,
            validation_error=error,
            llm=model,
        ),
    )


def build_resume_extraction_chain(llm: Any):
    return RESUME_EXTRACTION_PROMPT | llm.with_structured_output(_resume_profile_schema())


def build_resume_extraction_repair_chain(llm: Any):
    return RESUME_EXTRACTION_REPAIR_PROMPT | llm.with_structured_output(
        _resume_profile_schema()
    )


def repair_resume_profile_output(
    *,
    resume_text: str,
    invalid_output: Any,
    validation_error: Exception,
    llm: Any,
) -> Any:
    return build_resume_extraction_repair_chain(llm).invoke(
        {
            "resume_text": resume_text,
            "invalid_output": _json_dump(invalid_output),
            "validation_errors": _json_dump(_validation_error_details(validation_error)),
        }
    )


def create_resume_extraction_llm() -> Any:
    if not settings.resume_extraction_model:
        raise RuntimeError(
            "RESUME_EXTRACTION_MODEL must be set when RESUME_EXTRACTION_MODE=llm."
        )

    try:
        from langchain.chat_models import init_chat_model
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The langchain package is required for LLM resume extraction."
        ) from exc

    return init_chat_model(
        settings.resume_extraction_model,
        temperature=0,
    )


def _validation_error_details(validation_error: Exception) -> Any:
    errors = getattr(validation_error, "errors", None)
    if callable(errors):
        return errors(include_input=False)
    return str(validation_error)


def _json_dump(value: Any) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def _resume_profile_schema() -> dict[str, Any]:
    return ResumeProfile.model_json_schema()
