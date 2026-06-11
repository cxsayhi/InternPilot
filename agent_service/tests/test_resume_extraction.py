import pytest
from langchain_core.runnables import RunnableLambda

from app.schemas.project import ProjectEvidence
from app.schemas.resume import ResumeProfile
from app.schemas.run import LLM_OUTPUT_VALIDATION_FAILED
from app.services.resume_extraction import extract_resume_profile_from_text
from app.services.structured_output import StructuredOutputValidationError


class FakeStructuredLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.schemas = []

    def with_structured_output(self, schema):
        self.schemas.append(schema)
        return RunnableLambda(lambda _input: self.responses.pop(0))


def test_extract_resume_profile_returns_validated_resume_profile_with_evidence():
    llm = FakeStructuredLLM(
        [
            {
                "education": ["B.S. Computer Science, Demo University"],
                "skills": ["Java", "Spring Boot", "MySQL"],
                "skill_evidence": {
                    "Java": ["Built a Java backend for an online shopping platform."],
                    "Spring Boot": ["Built a Java backend with Spring Boot."],
                },
                "projects": [
                    {
                        "name": "Online Shopping Platform",
                        "description": "Spring Boot backend project.",
                        "tech_stack": ["Java", "Spring Boot", "MySQL"],
                        "evidence_text": "Built a Java backend with Spring Boot and MySQL.",
                        "source": "resume_project",
                    }
                ],
                "work_experience": [],
                "evidence_bullets": [
                    "Built a Java backend with Spring Boot and MySQL."
                ],
                "weak_points": ["No Docker deployment evidence."],
            }
        ]
    )

    profile = extract_resume_profile_from_text("Built a Java backend.", llm=llm)

    assert profile.education == ["B.S. Computer Science, Demo University"]
    assert profile.skills == ["Java", "Spring Boot", "MySQL"]
    assert profile.skill_evidence["Java"]
    assert profile.projects[0].evidence_text == "Built a Java backend with Spring Boot and MySQL."
    assert profile.evidence_bullets
    assert profile.weak_points == ["No Docker deployment evidence."]
    assert "evidence_bullets" in llm.schemas[0]["properties"]


def test_extract_resume_profile_repairs_invalid_structured_output_once():
    llm = FakeStructuredLLM(
        [
            {
                "skills": ["Java"],
                "projects": [{"name": "Missing evidence text"}],
            },
            {
                "education": [],
                "skills": ["Java"],
                "skill_evidence": {
                    "Java": ["Built a Java backend."]
                },
                "projects": [
                    {
                        "name": "Backend Project",
                        "tech_stack": ["Java"],
                        "evidence_text": "Built a Java backend.",
                        "source": "resume_project",
                    }
                ],
                "work_experience": [],
                "evidence_bullets": ["Built a Java backend."],
                "weak_points": [],
            },
        ]
    )

    profile = extract_resume_profile_from_text("Built a Java backend.", llm=llm)

    assert profile.projects[0].name == "Backend Project"
    assert len(llm.schemas) == 2


def test_extract_resume_profile_returns_stable_error_after_failed_repair():
    llm = FakeStructuredLLM(
        [
            {
                "skills": ["Java"],
                "projects": [{"name": "Missing evidence text"}],
            },
            {
                "skills": ["Java"],
                "projects": [{"name": "Still missing evidence text"}],
            },
        ]
    )

    with pytest.raises(StructuredOutputValidationError) as exc_info:
        extract_resume_profile_from_text("Built a Java backend.", llm=llm)

    assert exc_info.value.error.code == LLM_OUTPUT_VALIDATION_FAILED
    assert len(llm.schemas) == 2


def test_resume_profile_accepts_existing_alias_payloads():
    profile = ResumeProfile.model_validate(
        {
            "skills": ["Java"],
            "bullets": ["Built a Java backend."],
            "experiences": ["Software Engineering Intern"],
            "weakPoints": ["No deployment evidence."],
            "skillEvidence": {"Java": ["Built a Java backend."]},
        }
    )
    project = ProjectEvidence.model_validate(
        {
            "projectId": "p1",
            "techStack": ["Java"],
            "evidenceText": "Built a Java backend.",
        }
    )

    assert profile.evidence_bullets == ["Built a Java backend."]
    assert profile.bullets == ["Built a Java backend."]
    assert profile.work_experience == ["Software Engineering Intern"]
    assert profile.experiences == ["Software Engineering Intern"]
    assert profile.weak_points == ["No deployment evidence."]
    assert profile.skill_evidence["Java"]
    assert project.project_id == "p1"
    assert project.tech_stack == ["Java"]
    assert project.evidence_text == "Built a Java backend."
