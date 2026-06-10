from app.graphs.application_graph import run_application_graph
from app.schemas.analysis import ApplicationAnalysisRequest


def test_application_graph_returns_core_analysis():
    request = ApplicationAnalysisRequest(
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
    assert response.rewriteSuggestions
    assert len(response.learningPlan) == 7

