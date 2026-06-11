from app.graphs.application_graph import (
    compare_skills,
    extract_job_requirements,
    extract_resume_profile,
    generate_learning_plan,
    generate_resume_rewrites,
    prepare_response,
    validate_input,
)
from app.schemas.job import JobProfile
from app.schemas.match import MatchResult
from app.schemas.plan import LearningPlanItem
from app.schemas.resume import ResumeProfile
from app.schemas.rewrite import RewriteSuggestion
from app.schemas.run import AnalyzeApplicationResponse


def test_mvp_workflow_nodes_return_typed_partial_state_without_mutating_input():
    state = {
        "run_id": "run_test",
        "user_id": "user_1",
        "application_id": "app_1",
        "resume_text": "Built a Java backend with Spring Boot and MySQL.",
        "job_text": "Java Backend Intern requirements: Java, Spring Boot, MySQL, Docker.",
        "company": "Demo",
        "role": "Java Backend Intern",
        "warnings": [],
        "errors": [],
    }

    validation_update = validate_input(state)
    assert set(validation_update) == {"errors"}
    assert "job_profile" not in state

    state = {**state, **validation_update}
    job_update = extract_job_requirements(state)
    assert set(job_update) == {"job_profile"}
    assert isinstance(job_update["job_profile"], JobProfile)
    assert "job_profile" not in state

    state = {**state, **job_update}
    resume_update = extract_resume_profile(state)
    assert set(resume_update) == {"resume_profile"}
    assert isinstance(resume_update["resume_profile"], ResumeProfile)
    assert "resume_profile" not in state

    state = {**state, **resume_update}
    match_update = compare_skills(state)
    assert set(match_update) == {"match_result"}
    assert isinstance(match_update["match_result"], MatchResult)
    assert "match_result" not in state

    state = {**state, **match_update}
    rewrite_update = generate_resume_rewrites(state)
    assert set(rewrite_update) == {"rewrite_suggestions"}
    assert isinstance(rewrite_update["rewrite_suggestions"][0], RewriteSuggestion)
    assert "rewrite_suggestions" not in state

    state = {**state, **rewrite_update}
    plan_update = generate_learning_plan(state)
    assert set(plan_update) == {"learning_plan"}
    assert isinstance(plan_update["learning_plan"][0], LearningPlanItem)
    assert "learning_plan" not in state

    state = {**state, **plan_update}
    response_update = prepare_response(state)
    assert set(response_update) == {"response"}
    assert isinstance(response_update["response"], AnalyzeApplicationResponse)
    assert "response" not in state
