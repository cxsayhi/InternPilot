from __future__ import annotations

import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.schemas.job import JobProfile
from app.services.structured_output import validate_structured_output


JOB_EXTRACTION_PROMPT_VERSION = "langchain_job_extraction.v1"
JOB_EXTRACTION_REPAIR_PROMPT_VERSION = "langchain_job_extraction_repair.v1"

JOB_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You extract internship job descriptions into a strict JobProfile. "
            "Return only facts supported by the job text. Do not infer skills, "
            "company names, seniority, or responsibilities that are not present.",
        ),
        (
            "human",
            "Extract this job description.\n\n"
            "Required output fields:\n"
            "- role_title\n"
            "- company\n"
            "- required_skills\n"
            "- preferred_skills\n"
            "- responsibilities\n"
            "- keywords\n"
            "- seniority\n\n"
            "Job description:\n{job_text}",
        ),
    ]
)

JOB_EXTRACTION_REPAIR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Repair a failed structured JobProfile extraction. Keep only facts "
            "supported by the original job text and return a valid JobProfile.",
        ),
        (
            "human",
            "Original job description:\n{job_text}\n\n"
            "Invalid output:\n{invalid_output}\n\n"
            "Pydantic validation errors:\n{validation_errors}\n\n"
            "Return a corrected JobProfile.",
        ),
    ]
)


def extract_job_profile(job_text: str, llm: Any | None = None) -> JobProfile:
    model = llm or create_job_extraction_llm()
    raw_output = build_job_extraction_chain(model).invoke({"job_text": job_text})

    return validate_structured_output(
        JobProfile,
        raw_output,
        repair_fn=lambda payload, error: repair_job_profile_output(
            job_text=job_text,
            invalid_output=payload,
            validation_error=error,
            llm=model,
        ),
    )


def build_job_extraction_chain(llm: Any):
    return JOB_EXTRACTION_PROMPT | llm.with_structured_output(_job_profile_schema())


def build_job_extraction_repair_chain(llm: Any):
    return JOB_EXTRACTION_REPAIR_PROMPT | llm.with_structured_output(_job_profile_schema())


def repair_job_profile_output(
    *,
    job_text: str,
    invalid_output: Any,
    validation_error: Exception,
    llm: Any,
) -> Any:
    return build_job_extraction_repair_chain(llm).invoke(
        {
            "job_text": job_text,
            "invalid_output": _json_dump(invalid_output),
            "validation_errors": _json_dump(_validation_error_details(validation_error)),
        }
    )


def create_job_extraction_llm() -> Any:
    if not settings.job_extraction_model:
        raise RuntimeError(
            "JOB_EXTRACTION_MODEL must be set when JOB_EXTRACTION_MODE=llm."
        )

    try:
        from langchain.chat_models import init_chat_model
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The langchain package is required for LLM job extraction."
        ) from exc

    return init_chat_model(
        settings.job_extraction_model,
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


def _job_profile_schema() -> dict[str, Any]:
    return JobProfile.model_json_schema()
