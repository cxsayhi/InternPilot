import pytest
from langchain_core.runnables import RunnableLambda

from app.schemas.job import JobProfile
from app.schemas.run import LLM_OUTPUT_VALIDATION_FAILED
from app.services.job_extraction import extract_job_profile
from app.services.structured_output import StructuredOutputValidationError


class FakeStructuredLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.schemas = []

    def with_structured_output(self, schema):
        self.schemas.append(schema)
        return RunnableLambda(lambda _input: self.responses.pop(0))


def test_extract_job_profile_returns_validated_job_profile():
    llm = FakeStructuredLLM(
        [
            {
                "role_title": "Java Backend Intern",
                "company": "Demo",
                "required_skills": ["Java", "Spring Boot", "MySQL"],
                "preferred_skills": ["RAG"],
                "responsibilities": ["Build REST APIs for backend services."],
                "keywords": ["Java", "Spring Boot", "REST API"],
                "seniority": "intern",
            }
        ]
    )

    profile = extract_job_profile("Java Backend Intern at Demo", llm=llm)

    assert profile.role_title == "Java Backend Intern"
    assert profile.company == "Demo"
    assert profile.required_skills == ["Java", "Spring Boot", "MySQL"]
    assert profile.preferred_skills == ["RAG"]
    assert profile.seniority == "intern"
    assert "required_skills" in llm.schemas[0]["properties"]


def test_extract_job_profile_repairs_invalid_structured_output_once():
    llm = FakeStructuredLLM(
        [
            {"required_skills": [{"name": "Java"}]},
            {
                "role_title": "Java Backend Intern",
                "company": None,
                "required_skills": ["Java"],
                "preferred_skills": [],
                "responsibilities": [],
                "keywords": ["Java"],
                "seniority": "intern",
            },
        ]
    )

    profile = extract_job_profile("Java Backend Intern requirements: Java", llm=llm)

    assert profile.required_skills == ["Java"]
    assert len(llm.schemas) == 2


def test_extract_job_profile_returns_stable_error_after_failed_repair():
    llm = FakeStructuredLLM(
        [
            {"required_skills": [{"name": "Java"}]},
            {"required_skills": [{"name": "Java"}]},
        ]
    )

    with pytest.raises(StructuredOutputValidationError) as exc_info:
        extract_job_profile("Java Backend Intern requirements: Java", llm=llm)

    assert exc_info.value.error.code == LLM_OUTPUT_VALIDATION_FAILED
    assert len(llm.schemas) == 2


def test_job_profile_accepts_existing_camel_case_payloads():
    profile = JobProfile.model_validate(
        {
            "role": "Backend Intern",
            "requiredSkills": ["Java"],
            "preferredSkills": ["RAG"],
            "extractedSkills": [{"name": "Docker", "evidenceText": "Docker"}],
        }
    )

    assert profile.role_title == "Backend Intern"
    assert profile.required_skills == ["Java"]
    assert profile.preferred_skills == ["RAG"]
    assert profile.extracted_skills[0].evidence_text == "Docker"
