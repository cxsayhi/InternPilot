from __future__ import annotations

from app.schemas.match import MatchResult, SkillMatch
from app.schemas.project import ProjectEvidence
from app.schemas.resume import ResumeProfile
from app.schemas.rewrite import RewriteSuggestion
from app.services.skill_matching import find_known_skills, is_skill_inventory_line
from app.services.structured_output import validate_structured_output


FORBIDDEN_FABRICATION_CLAIMS = [
    "certification",
    "company",
    "deployed",
    "launched",
    "production",
    "users",
    "metrics",
]


def generate_no_fabrication_rewrites(
    resume_profile: ResumeProfile,
    match_result: MatchResult,
    *,
    max_suggestions: int = 3,
) -> list[RewriteSuggestion]:
    strong_matches = {
        match.skill: match
        for match in match_result.strongMatches
        if _has_resume_or_project_evidence(match)
    }
    blocked_skills = {
        match.skill
        for match in [*match_result.weakMatches, *match_result.missingSkills]
    }

    suggestions: list[RewriteSuggestion] = []
    seen_originals: set[str] = set()

    for original, source in _candidate_evidence_lines(resume_profile):
        if original in seen_originals or is_skill_inventory_line(original):
            continue

        targeted_skills = _targeted_skills_for_line(
            original,
            strong_matches=strong_matches,
            blocked_skills=blocked_skills,
        )
        if not targeted_skills:
            continue

        evidence_sources = _evidence_sources_for_line(
            original=original,
            source=source,
            targeted_skills=targeted_skills,
            strong_matches=strong_matches,
        )
        rewritten = _rewrite_from_supported_evidence(original, targeted_skills)
        unsupported_claims = _unsupported_claims(
            rewritten_bullet=rewritten,
            original_bullet=original,
            blocked_skills=blocked_skills,
        )

        if unsupported_claims:
            continue

        suggestion = validate_structured_output(
            RewriteSuggestion,
            {
                "originalBullet": original,
                "rewrittenBullet": rewritten,
                "targetedSkills": targeted_skills,
                "evidenceSources": evidence_sources,
                "unsupportedClaims": [],
                "confidence": _confidence_for_sources(evidence_sources),
                "needsUserConfirmation": True,
            },
        )
        suggestions.append(suggestion)
        seen_originals.add(original)

        if len(suggestions) >= max_suggestions:
            break

    return suggestions


def _candidate_evidence_lines(
    resume_profile: ResumeProfile,
) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []

    for bullet in resume_profile.evidence_bullets:
        if bullet.strip():
            candidates.append((bullet.strip(), "resume:evidence_bullet"))

    for index, project in enumerate(resume_profile.projects, start=1):
        if project.evidence_text.strip():
            source = project.name or project.project_id or f"project_{index}"
            candidates.append((project.evidence_text.strip(), f"project:{source}"))

    for index, experience in enumerate(resume_profile.work_experience, start=1):
        if experience.strip():
            candidates.append((experience.strip(), f"resume:work_experience_{index}"))

    return candidates


def _targeted_skills_for_line(
    line: str,
    *,
    strong_matches: dict[str, SkillMatch],
    blocked_skills: set[str],
) -> list[str]:
    line_skills = set(find_known_skills(line))
    targeted: list[str] = []

    for skill, match in strong_matches.items():
        if skill in blocked_skills:
            continue
        if skill in line_skills or _match_has_line_evidence(match, line):
            targeted.append(skill)

    return sorted(targeted)


def _evidence_sources_for_line(
    *,
    original: str,
    source: str,
    targeted_skills: list[str],
    strong_matches: dict[str, SkillMatch],
) -> list[str]:
    sources = [f"{source}: {original}"]
    for skill in targeted_skills:
        for evidence in strong_matches[skill].evidence:
            if _evidence_supports_line(evidence.text, original):
                sources.append(f"{evidence.source}: {evidence.text}")

    return list(dict.fromkeys(sources))


def _rewrite_from_supported_evidence(original: str, targeted_skills: list[str]) -> str:
    cleaned = original.strip().rstrip(".")
    missing_skill_names = [
        skill
        for skill in targeted_skills
        if skill.lower() not in cleaned.lower()
    ]

    if missing_skill_names:
        return f"{cleaned} using {', '.join(missing_skill_names)}."
    return f"{cleaned}."


def _unsupported_claims(
    *,
    rewritten_bullet: str,
    original_bullet: str,
    blocked_skills: set[str],
) -> list[str]:
    unsupported: list[str] = []
    rewritten_lower = rewritten_bullet.lower()
    original_lower = original_bullet.lower()

    for skill in blocked_skills:
        if skill.lower() in rewritten_lower and skill.lower() not in original_lower:
            unsupported.append(f"Unsupported skill claim: {skill}")

    for claim in FORBIDDEN_FABRICATION_CLAIMS:
        if claim in rewritten_lower and claim not in original_lower:
            unsupported.append(f"Unsupported claim category: {claim}")

    return unsupported


def _confidence_for_sources(evidence_sources: list[str]) -> float:
    if any(source.startswith("project:") for source in evidence_sources):
        return 0.9
    if any(source.startswith("resume:evidence_bullet") for source in evidence_sources):
        return 0.82
    return 0.72


def _match_has_line_evidence(match: SkillMatch, line: str) -> bool:
    return any(_evidence_supports_line(evidence.text, line) for evidence in match.evidence)


def _evidence_supports_line(evidence_text: str, line: str) -> bool:
    return evidence_text == line or evidence_text.endswith(f": {line}")


def _has_resume_or_project_evidence(match: SkillMatch) -> bool:
    return any(
        evidence.source.startswith(("project", "resume_bullet", "resume_experience"))
        for evidence in match.evidence
    )
