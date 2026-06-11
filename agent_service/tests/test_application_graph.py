from app.graphs.application_graph import run_application_graph
from app.graphs import application_graph
from app.schemas.job import JobProfile
from app.schemas.run import AnalyzeApplicationRequest
from app.services.job_extraction import JOB_EXTRACTION_PROMPT_VERSION


def test_application_graph_returns_core_analysis():
    request = AnalyzeApplicationRequest(
        userId="user_1",
        applicationId="app_1",
        resumeText="Built an online shopping platform with Java, Spring Boot, MySQL, Redis, and Git.",
        jobText="Java Backend Intern requirements: Spring Boot, MySQL, Redis, Docker, REST API, Git, RAG.",
        company="Demo",
        role="Java Backend Intern",
    )

    response = run_application_graph(request)

    assert response.matchScore > 0
    assert response.strongMatches
    assert response.missingSkills
    assert "projectEvidenceStrength" in response.scoreBreakdown
    assert response.rewriteSuggestions
    assert len(response.learningPlan) == 7


def test_application_graph_uses_llm_job_extraction_when_enabled(monkeypatch):
    monkeypatch.setattr(application_graph.settings, "job_extraction_mode", "llm")
    monkeypatch.setattr(
        application_graph,
        "extract_job_profile",
        lambda _job_text: JobProfile(
            role_title="Java Backend Intern",
            company="Demo",
            required_skills=["Java", "Spring Boot"],
            preferred_skills=["RAG"],
            responsibilities=["Build backend APIs."],
            keywords=["Java", "Spring Boot", "RAG"],
            seniority="intern",
        ),
    )

    request = AnalyzeApplicationRequest(
        userId="user_1",
        applicationId="app_1",
        resumeText="Built a Java backend with Spring Boot.",
        jobText="This text is parsed by the mocked LLM extractor.",
    )

    response = run_application_graph(request)

    assert response.metadata.promptVersions["jobExtraction"] == JOB_EXTRACTION_PROMPT_VERSION
    assert {match.skill for match in response.strongMatches} == {"Java", "Spring Boot"}
    assert {match.skill for match in response.missingSkills} == {"RAG"}
