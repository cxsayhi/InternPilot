from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api import routes_analysis
from app.main import app
from app.schemas.match import MatchResult
from app.schemas.run import AgentError, LLM_OUTPUT_VALIDATION_FAILED
from app.services.structured_output import StructuredOutputValidationError


def test_analysis_route_returns_stable_error_code_for_validation_failure(monkeypatch):
    def raise_validation_error(_request):
        try:
            MatchResult.model_validate({"score": 101})
        except ValidationError as validation_error:
            raise StructuredOutputValidationError(
                AgentError(
                    code=LLM_OUTPUT_VALIDATION_FAILED,
                    message="Structured output failed validation for MatchResult.",
                    retryable=False,
                ),
                validation_error,
            ) from validation_error

    monkeypatch.setattr(routes_analysis, "run_application_graph", raise_validation_error)

    client = TestClient(app)
    response = client.post(
        "/internal/agent/application-analysis",
        json={
            "userId": "user_1",
            "applicationId": "app_1",
            "resumeText": "Built a Java backend.",
            "jobText": "Java Backend Intern.",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == LLM_OUTPUT_VALIDATION_FAILED
