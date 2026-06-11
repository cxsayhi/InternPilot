from __future__ import annotations

import re
from collections.abc import Iterable

from app.schemas.job import JobProfile
from app.schemas.match import MatchResult, SkillEvidence, SkillMatch
from app.schemas.project import ProjectEvidence
from app.schemas.resume import ResumeProfile
from app.services.structured_output import validate_structured_output


SCORE_WEIGHTS = {
    "requiredSkillCoverage": 40,
    "preferredSkillCoverage": 15,
    "projectEvidenceStrength": 20,
    "responsibilityAlignment": 15,
    "resumeKeywordClarity": 10,
}

KNOWN_SKILLS = [
    "Java",
    "Spring Boot",
    "MySQL",
    "Redis",
    "Docker",
    "REST API",
    "Git",
    "LLM",
    "RAG",
    "CI/CD",
    "Testing",
    "Vue",
    "React",
    "Python",
    "FastAPI",
]

SKILL_ALIASES = {
    "CI/CD": ["ci cd", "cicd", "continuous integration", "continuous deployment"],
    "FastAPI": ["fast api"],
    "Git": ["github", "gitlab"],
    "LLM": ["large language model", "large language models", "generative ai"],
    "MySQL": ["sql", "relational database"],
    "RAG": ["retrieval augmented generation", "retrieval augmentation"],
    "REST API": ["rest", "rest api", "restful api", "restful apis"],
    "Spring Boot": ["springboot", "spring"],
    "Testing": ["test", "tests", "unit test", "integration test", "api test"],
    "Vue": ["vue3", "vue.js"],
}

PREFERRED_MARKERS = (
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "plus",
    "familiarity",
)


def calculate_skill_match(
    job_profile: JobProfile,
    resume_profile: ResumeProfile,
    projects: list[ProjectEvidence],
) -> MatchResult:
    required_skills = _dedupe_skills(
        [
            *job_profile.required_skills,
            *[
                skill.name
                for skill in job_profile.extracted_skills
                if skill.importance == "required"
            ],
        ]
    )
    preferred_skills = _dedupe_skills(
        [
            *job_profile.preferred_skills,
            *[
                skill.name
                for skill in job_profile.extracted_skills
                if skill.importance in {"preferred", "bonus"}
            ],
        ]
    )
    preferred_skills = [
        skill
        for skill in preferred_skills
        if _skill_key(skill) not in {_skill_key(required) for required in required_skills}
    ]
    target_skills = _dedupe_skills([*required_skills, *preferred_skills])

    if not target_skills:
        return validate_structured_output(
            MatchResult,
            {
                "score": 0,
                "breakdown": {key: 0 for key in SCORE_WEIGHTS},
                "strongMatches": [],
                "weakMatches": [],
                "missingSkills": [],
            },
        )

    evidence_by_skill = {
        skill: _collect_skill_evidence(skill, resume_profile, projects)
        for skill in target_skills
    }

    strong_matches: list[SkillMatch] = []
    weak_matches: list[SkillMatch] = []
    missing_skills: list[SkillMatch] = []
    skill_strength: dict[str, float] = {}

    for skill in target_skills:
        evidence = evidence_by_skill[skill]
        if not evidence:
            missing_skills.append(_missing_skill_match(skill))
            skill_strength[_skill_key(skill)] = 0.0
        elif _has_contextual_evidence(evidence):
            strong_matches.append(_skill_match(skill, "matched", evidence))
            skill_strength[_skill_key(skill)] = 1.0
        else:
            weak_matches.append(_skill_match(skill, "weak", evidence))
            skill_strength[_skill_key(skill)] = 0.4

    breakdown = {
        "requiredSkillCoverage": _coverage_score(
            required_skills,
            skill_strength,
            SCORE_WEIGHTS["requiredSkillCoverage"],
            default_full=bool(target_skills),
        ),
        "preferredSkillCoverage": _coverage_score(
            preferred_skills,
            skill_strength,
            SCORE_WEIGHTS["preferredSkillCoverage"],
            default_full=bool(target_skills),
        ),
        "projectEvidenceStrength": _project_evidence_score(
            target_skills,
            evidence_by_skill,
        ),
        "responsibilityAlignment": _responsibility_alignment_score(
            job_profile,
            resume_profile,
            projects,
            target_skills,
            evidence_by_skill,
        ),
        "resumeKeywordClarity": _resume_keyword_clarity_score(
            target_skills,
            evidence_by_skill,
        ),
    }

    return validate_structured_output(
        MatchResult,
        {
            "score": min(100, sum(breakdown.values())),
            "breakdown": breakdown,
            "strongMatches": strong_matches,
            "weakMatches": weak_matches,
            "missingSkills": missing_skills,
        },
    )


def find_known_skills(text: str) -> list[str]:
    return [
        skill
        for skill in KNOWN_SKILLS
        if _contains_any_alias(text, skill)
    ]


def is_preferred_skill_line(line: str) -> bool:
    normalized = _normalize_text(line)
    return any(marker in normalized for marker in PREFERRED_MARKERS)


def is_skill_inventory_line(line: str) -> bool:
    normalized = _normalize_text(line)
    return normalized.startswith(
        (
            "skill",
            "skills",
            "technical skills",
            "technologies",
            "tech stack",
        )
    )


def _collect_skill_evidence(
    skill: str,
    resume_profile: ResumeProfile,
    projects: list[ProjectEvidence],
) -> list[SkillEvidence]:
    evidence: list[SkillEvidence] = []

    for resume_skill in resume_profile.skills:
        if _same_skill(skill, resume_skill):
            evidence.append(
                SkillEvidence(
                    source="resume_skill",
                    text=f"Resume skills list includes {resume_skill}.",
                )
            )

    for bullet in resume_profile.bullets:
        if _contains_any_alias(bullet, skill) and not is_skill_inventory_line(bullet):
            evidence.append(SkillEvidence(source="resume_bullet", text=bullet))

    for experience in resume_profile.experiences:
        if _contains_any_alias(experience, skill):
            evidence.append(SkillEvidence(source="resume_experience", text=experience))

    for project in projects:
        evidence.extend(_project_skill_evidence(skill, project))

    return _dedupe_evidence(evidence)


def _project_skill_evidence(skill: str, project: ProjectEvidence) -> list[SkillEvidence]:
    evidence: list[SkillEvidence] = []
    source = _project_source(project)

    for tech in project.techStack:
        if _same_skill(skill, tech):
            evidence.append(
                SkillEvidence(
                    source=source,
                    text=f"Project tech stack includes {tech}: {project.evidenceText}",
                )
            )

    project_text = " ".join(
        part
        for part in [
            project.name,
            project.description,
            project.evidenceText,
        ]
        if part
    )
    if _contains_any_alias(project_text, skill):
        evidence.append(SkillEvidence(source=source, text=project.evidenceText))

    return evidence


def _missing_skill_match(skill: str) -> SkillMatch:
    return SkillMatch(
        skill=skill,
        status="missing",
        evidence=[
            SkillEvidence(
                source="job_description",
                text=f"{skill} appears in the job requirements, but no resume or project evidence was found.",
            )
        ],
        confidence=0.0,
    )


def _skill_match(
    skill: str,
    status: str,
    evidence: list[SkillEvidence],
) -> SkillMatch:
    confidence = 0.9 if status == "matched" else 0.55
    return SkillMatch(
        skill=skill,
        status=status,
        evidence=evidence,
        confidence=confidence,
    )


def _coverage_score(
    skills: list[str],
    skill_strength: dict[str, float],
    max_score: int,
    *,
    default_full: bool,
) -> int:
    if not skills:
        return max_score if default_full else 0

    coverage = sum(skill_strength.get(_skill_key(skill), 0.0) for skill in skills)
    return round(max_score * coverage / len(skills))


def _project_evidence_score(
    target_skills: list[str],
    evidence_by_skill: dict[str, list[SkillEvidence]],
) -> int:
    covered = sum(
        1
        for skill in target_skills
        if any(evidence.source.startswith("project") for evidence in evidence_by_skill[skill])
    )
    return round(SCORE_WEIGHTS["projectEvidenceStrength"] * covered / len(target_skills))


def _responsibility_alignment_score(
    job_profile: JobProfile,
    resume_profile: ResumeProfile,
    projects: list[ProjectEvidence],
    target_skills: list[str],
    evidence_by_skill: dict[str, list[SkillEvidence]],
) -> int:
    resume_texts = [
        *resume_profile.bullets,
        *resume_profile.experiences,
        *[project.evidenceText for project in projects],
    ]
    responsibilities = [
        responsibility
        for responsibility in job_profile.responsibilities
        if responsibility.strip()
    ]

    if responsibilities and resume_texts:
        alignment = sum(
            _best_token_overlap(responsibility, resume_texts)
            for responsibility in responsibilities
        ) / len(responsibilities)
        return round(SCORE_WEIGHTS["responsibilityAlignment"] * alignment)

    contextual = sum(
        1
        for skill in target_skills
        if _has_contextual_evidence(evidence_by_skill[skill])
    )
    return round(SCORE_WEIGHTS["responsibilityAlignment"] * contextual / len(target_skills))


def _resume_keyword_clarity_score(
    target_skills: list[str],
    evidence_by_skill: dict[str, list[SkillEvidence]],
) -> int:
    mentioned = sum(1 for skill in target_skills if evidence_by_skill[skill])
    return round(SCORE_WEIGHTS["resumeKeywordClarity"] * mentioned / len(target_skills))


def _best_token_overlap(text: str, candidates: list[str]) -> float:
    text_tokens = _content_tokens(text)
    if not text_tokens:
        return 0.0
    return max(
        (
            len(text_tokens & _content_tokens(candidate)) / len(text_tokens)
            for candidate in candidates
        ),
        default=0.0,
    )


def _content_tokens(text: str) -> set[str]:
    stop_words = {
        "a",
        "an",
        "and",
        "for",
        "in",
        "of",
        "or",
        "the",
        "to",
        "with",
    }
    return {
        token
        for token in _normalize_text(text).split()
        if len(token) > 2 and token not in stop_words
    }


def _has_contextual_evidence(evidence: list[SkillEvidence]) -> bool:
    return any(
        item.source.startswith(("project", "resume_bullet", "resume_experience"))
        for item in evidence
    )


def _dedupe_skills(skills: Iterable[str]) -> list[str]:
    result: dict[str, str] = {}
    for skill in skills:
        canonical = _canonical_skill(skill)
        if canonical:
            result.setdefault(_skill_key(canonical), canonical)
    return list(result.values())


def _dedupe_evidence(evidence: list[SkillEvidence]) -> list[SkillEvidence]:
    result: dict[tuple[str, str], SkillEvidence] = {}
    for item in evidence:
        result.setdefault((item.source, item.text), item)
    return list(result.values())


def _project_source(project: ProjectEvidence) -> str:
    label = project.name or project.projectId or project.source
    return f"project:{label}"


def _same_skill(left: str, right: str) -> bool:
    return _skill_key(left) == _skill_key(right)


def _skill_key(skill: str) -> str:
    return _normalize_text(_canonical_skill(skill))


def _canonical_skill(skill: str) -> str:
    normalized_skill = _normalize_text(skill)
    for known_skill in KNOWN_SKILLS:
        aliases = [_normalize_text(known_skill), *[_normalize_text(alias) for alias in SKILL_ALIASES.get(known_skill, [])]]
        if normalized_skill in aliases:
            return known_skill
    return skill.strip()


def _contains_any_alias(text: str, skill: str) -> bool:
    normalized_text = _normalize_text(text)
    aliases = [_canonical_skill(skill), *SKILL_ALIASES.get(_canonical_skill(skill), [])]
    return any(_contains_phrase(normalized_text, _normalize_text(alias)) for alias in aliases)


def _contains_phrase(normalized_text: str, normalized_phrase: str) -> bool:
    if not normalized_phrase:
        return False
    return re.search(rf"(^|\s){re.escape(normalized_phrase)}(\s|$)", normalized_text) is not None


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()
