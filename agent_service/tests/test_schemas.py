import pytest
from pydantic import ValidationError

from app.schemas.match import MatchResult, SkillMatch
from app.schemas.plan import LearningPlanItem
from app.schemas.run import (
    LLM_OUTPUT_VALIDATION_FAILED,
    AgentMetadata,
    AnalyzeApplicationResponse,
)
from app.schemas.rewrite import RewriteSuggestion
from app.services.structured_output import (
    StructuredOutputValidationError,
    validate_structured_output,
)


def test_analyze_application_response_accepts_structured_payload():
    response = AnalyzeApplicationResponse(
        runId="run_1",
        matchScore=78,
        scoreBreakdown={"requiredSkillCoverage": 32},
        strongMatches=[
            {
                "skill": "Java",
                "status": "matched",
                "evidence": [
                    {
                        "source": "pasted_resume_text",
                        "text": "Resume mentions Java.",
                    }
                ],
                "confidence": 0.92,
            }
        ],
        weakMatches=[],
        missingSkills=[],
        rewriteSuggestions=[
            {
                "originalBullet": "Built an online shopping platform.",
                "suggestedBullet": "Built a Java backend for an online shopping platform.",
                "targetedSkills": ["Java"],
                "evidenceSources": ["pasted_resume_text"],
                "unsupportedClaims": [],
                "confidence": 0.8,
                "needsUserConfirmation": False,
            }
        ],
        learningPlan=[
            {
                "day": 1,
                "title": "Improve Docker",
                "tasks": ["Add a Dockerfile."],
                "targetSkills": ["Docker"],
                "deliverable": "A runnable Dockerfile.",
            }
        ],
        metadata=AgentMetadata(
            graphVersion="phase4.test",
            model="deterministic",
            promptVersions={},
        ),
    )

    assert response.matchScore == 78
    assert response.strongMatches[0].skill == "Java"


def test_match_result_rejects_score_above_100():
    with pytest.raises(ValidationError):
        MatchResult(score=101)


def test_rewrite_suggestion_rejects_confidence_above_1():
    with pytest.raises(ValidationError):
        RewriteSuggestion(
            originalBullet="Built an online shopping platform.",
            suggestedBullet="Built a Java backend for an online shopping platform.",
            confidence=1.1,
            needsUserConfirmation=False,
        )


def test_learning_plan_item_rejects_day_above_7():
    with pytest.raises(ValidationError):
        LearningPlanItem(
            day=8,
            title="Improve Docker",
            tasks=["Add a Dockerfile."],
            deliverable="A runnable Dockerfile.",
        )


def test_skill_match_rejects_unknown_status():
    with pytest.raises(ValidationError):
        SkillMatch(
            skill="Docker",
            status="partial",
            evidence=[],
            confidence=0.7,
        )


def test_structured_output_validation_retries_repair_once_then_returns_agent_error():
    repair_calls = []

    def repair(payload, _validation_error):
        repair_calls.append(payload)
        return payload

    with pytest.raises(StructuredOutputValidationError) as exc_info:
        validate_structured_output(MatchResult, {"score": 101}, repair_fn=repair)

    assert len(repair_calls) == 1
    assert exc_info.value.error.code == LLM_OUTPUT_VALIDATION_FAILED
