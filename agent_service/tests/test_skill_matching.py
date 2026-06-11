from app.schemas.job import JobProfile
from app.schemas.project import ProjectEvidence
from app.schemas.resume import ResumeProfile
from app.services.skill_matching import SCORE_WEIGHTS, calculate_skill_match


def test_calculate_skill_match_requires_contextual_evidence_for_strong_match():
    result = calculate_skill_match(
        job_profile=JobProfile(
            requiredSkills=["Java", "Docker"],
            preferredSkills=["RAG"],
        ),
        resume_profile=ResumeProfile(
            skills=["Java", "Docker"],
            bullets=["Built an online shopping platform with Java and Spring Boot."],
        ),
        projects=[
            ProjectEvidence(
                name="Shopping Platform",
                techStack=["Java"],
                evidenceText="Built an online shopping platform with Java and Spring Boot.",
            )
        ],
    )

    strong_skills = {match.skill for match in result.strongMatches}
    weak_skills = {match.skill for match in result.weakMatches}
    missing_skills = {match.skill for match in result.missingSkills}

    assert "Java" in strong_skills
    assert "Docker" not in strong_skills
    assert "Docker" in weak_skills
    assert "RAG" in missing_skills
    assert result.weakMatches[0].evidence
    assert result.missingSkills[0].evidence[0].source == "job_description"


def test_calculate_skill_match_does_not_treat_skill_inventory_as_strong_evidence():
    result = calculate_skill_match(
        job_profile=JobProfile(requiredSkills=["Java", "Docker"]),
        resume_profile=ResumeProfile(
            skills=["Java", "Docker"],
            bullets=["Skills: Java, Docker"],
        ),
        projects=[],
    )

    assert result.strongMatches == []
    assert {match.skill for match in result.weakMatches} == {"Java", "Docker"}


def test_calculate_skill_match_returns_explainable_weighted_score():
    result = calculate_skill_match(
        job_profile=JobProfile(
            requiredSkills=["Java", "Docker"],
            preferredSkills=["RAG"],
        ),
        resume_profile=ResumeProfile(
            skills=["Java", "Docker", "RAG"],
            bullets=[
                "Built a Java service with Docker deployment and RAG retrieval for internship matching."
            ],
        ),
        projects=[
            ProjectEvidence(
                name="InternPilot",
                techStack=["Java", "Docker", "RAG"],
                evidenceText="Built a Java service with Docker deployment and RAG retrieval.",
            )
        ],
    )

    assert result.score == 100
    assert result.breakdown == SCORE_WEIGHTS
    assert {match.skill for match in result.strongMatches} == {"Java", "Docker", "RAG"}
    assert result.weakMatches == []
    assert result.missingSkills == []


def test_calculate_skill_match_returns_zero_without_target_skills():
    result = calculate_skill_match(
        job_profile=JobProfile(),
        resume_profile=ResumeProfile(skills=["Java"]),
        projects=[],
    )

    assert result.score == 0
    assert result.breakdown == {key: 0 for key in SCORE_WEIGHTS}
    assert result.strongMatches == []
