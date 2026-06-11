from app.schemas.job import JobProfile
from app.schemas.project import ProjectEvidence
from app.schemas.resume import ResumeProfile
from app.schemas.rewrite import RewriteSuggestion
from app.services.resume_rewrite import generate_no_fabrication_rewrites
from app.services.skill_matching import calculate_skill_match


def test_rewrite_suggestion_accepts_rewritten_and_legacy_suggested_fields():
    rewritten = RewriteSuggestion(
        originalBullet="Built an online shopping platform.",
        rewrittenBullet="Built an online shopping platform using Java.",
        targetedSkills=["Java"],
        evidenceSources=["resume:evidence_bullet"],
        unsupportedClaims=[],
        confidence=0.8,
        needsUserConfirmation=True,
    )
    legacy = RewriteSuggestion(
        originalBullet="Built an online shopping platform.",
        suggestedBullet="Built an online shopping platform using Java.",
        targetedSkills=["Java"],
        evidenceSources=["resume:evidence_bullet"],
        unsupportedClaims=[],
        confidence=0.8,
        needsUserConfirmation=True,
    )

    assert rewritten.rewrittenBullet == "Built an online shopping platform using Java."
    assert rewritten.suggestedBullet == rewritten.rewrittenBullet
    assert legacy.rewrittenBullet == rewritten.rewrittenBullet


def test_no_fabrication_rewrite_excludes_missing_docker_claim():
    resume_profile = ResumeProfile(
        skills=["Java", "Spring Boot"],
        evidence_bullets=["Built an online shopping platform with Java and Spring Boot."],
        projects=[
            ProjectEvidence(
                name="Shopping Platform",
                tech_stack=["Java", "Spring Boot"],
                evidence_text="Built an online shopping platform with Java and Spring Boot.",
            )
        ],
    )
    match_result = calculate_skill_match(
        job_profile=JobProfile(
            required_skills=["Java", "Spring Boot", "Docker"],
        ),
        resume_profile=resume_profile,
        projects=resume_profile.projects,
    )

    suggestions = generate_no_fabrication_rewrites(resume_profile, match_result)

    assert suggestions
    assert all("Docker" not in suggestion.rewrittenBullet for suggestion in suggestions)
    assert all("Docker" not in suggestion.targetedSkills for suggestion in suggestions)
    assert all(suggestion.unsupportedClaims == [] for suggestion in suggestions)
    assert {match.skill for match in match_result.missingSkills} == {"Docker"}


def test_no_fabrication_rewrite_uses_only_existing_evidence():
    resume_profile = ResumeProfile(
        skills=["Java"],
        evidence_bullets=["Built an online shopping platform with Java."],
    )
    match_result = calculate_skill_match(
        job_profile=JobProfile(required_skills=["Java"]),
        resume_profile=resume_profile,
        projects=[],
    )

    suggestions = generate_no_fabrication_rewrites(resume_profile, match_result)

    assert suggestions[0].originalBullet == "Built an online shopping platform with Java."
    assert suggestions[0].rewrittenBullet == "Built an online shopping platform with Java."
    assert suggestions[0].targetedSkills == ["Java"]
    assert suggestions[0].evidenceSources
    assert suggestions[0].needsUserConfirmation is True


def test_no_fabrication_rewrite_returns_no_suggestion_without_source_evidence():
    resume_profile = ResumeProfile(skills=["Java"])
    match_result = calculate_skill_match(
        job_profile=JobProfile(required_skills=["Java"]),
        resume_profile=resume_profile,
        projects=[],
    )

    assert generate_no_fabrication_rewrites(resume_profile, match_result) == []
