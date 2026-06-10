from __future__ import annotations

from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from app.core.config import settings
from app.graphs.state import ApplicationAgentState
from app.schemas.analysis import (
    AgentMetadata,
    ApplicationAnalysisRequest,
    ApplicationAnalysisResponse,
    LearningPlanItem,
    RewriteSuggestion,
)

TECH_SKILLS = [
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


def run_application_graph(request: ApplicationAnalysisRequest) -> ApplicationAnalysisResponse:
    initial_state: ApplicationAgentState = {
        "run_id": f"run_{uuid4()}",
        "user_id": request.userId,
        "application_id": request.applicationId,
        "resume_text": request.resumeText,
        "job_text": request.jobText,
        "company": request.company,
        "role": request.role,
        "warnings": [],
        "errors": [],
    }

    final_state = _compiled_graph.invoke(initial_state)
    match_result = final_state["match_result"]

    return ApplicationAnalysisResponse(
        runId=final_state["run_id"],
        matchScore=match_result["score"],
        scoreBreakdown=match_result["breakdown"],
        strongMatches=match_result["strongMatches"],
        weakMatches=match_result["weakMatches"],
        missingSkills=match_result["missingSkills"],
        rewriteSuggestions=[
            RewriteSuggestion(**suggestion)
            for suggestion in final_state.get("rewrite_suggestions", [])
        ],
        learningPlan=[
            LearningPlanItem(**item)
            for item in final_state.get("learning_plan", [])
        ],
        warnings=final_state.get("warnings", []),
        metadata=AgentMetadata(
            graphVersion=settings.graph_version,
            model=settings.model_name,
            promptVersions={
                "jobExtraction": "deterministic_mvp.v1",
                "resumeExtraction": "deterministic_mvp.v1",
                "rewrite": "deterministic_mvp.v1",
                "learningPlan": "deterministic_mvp.v1",
            },
        ),
    )


def validate_input(state: ApplicationAgentState) -> ApplicationAgentState:
    errors: list[str] = []
    if not state.get("resume_text", "").strip():
        errors.append("RESUME_TEXT_EMPTY")
    if not state.get("job_text", "").strip():
        errors.append("JOB_TEXT_EMPTY")
    if errors:
        return {"errors": errors, "next_action": "failed"}
    return {"next_action": "extract_job"}


def extract_job_requirements(state: ApplicationAgentState) -> ApplicationAgentState:
    job_text = state["job_text"]
    required_skills = _find_skills(job_text)
    return {
        "job_profile": {
            "company": state.get("company"),
            "role": state.get("role"),
            "requiredSkills": required_skills,
            "keywords": required_skills,
        },
        "next_action": "extract_resume",
    }


def extract_resume_profile(state: ApplicationAgentState) -> ApplicationAgentState:
    resume_text = state["resume_text"]
    skills = _find_skills(resume_text)
    bullets = _extract_resume_bullets(resume_text)
    return {
        "resume_profile": {
            "skills": skills,
            "bullets": bullets,
        },
        "next_action": "match",
    }


def compare_skills(state: ApplicationAgentState) -> ApplicationAgentState:
    job_skills = set(state["job_profile"].get("requiredSkills", []))
    resume_skills = set(state["resume_profile"].get("skills", []))
    matched = sorted(job_skills & resume_skills)
    missing = sorted(job_skills - resume_skills)

    coverage = len(matched) / len(job_skills) if job_skills else 0
    required_score = round(coverage * 40)
    preferred_score = round(coverage * 15)
    evidence_score = round(min(len(matched), 4) / 4 * 20) if matched else 0
    responsibility_score = round(coverage * 15)
    clarity_score = 8 if matched else 2
    total = min(
        100,
        required_score
        + preferred_score
        + evidence_score
        + responsibility_score
        + clarity_score,
    )

    strong_matches = [
        _skill_item(skill, "matched", f"Found '{skill}' in both resume and job description.")
        for skill in matched
    ]
    missing_skills = [
        _skill_item(skill, "missing", f"'{skill}' appears in the job description but not in the resume text.")
        for skill in missing
    ]

    weak_matches = [
        item for item in missing_skills
        if item["skill"] in {"Docker", "RAG", "LLM", "CI/CD", "Testing"}
    ]

    return {
        "match_result": {
            "score": total,
            "breakdown": {
                "requiredSkillCoverage": required_score,
                "preferredSkillCoverage": preferred_score,
                "resumeEvidenceStrength": evidence_score,
                "responsibilityAlignment": responsibility_score,
                "resumeKeywordClarity": clarity_score,
            },
            "strongMatches": strong_matches,
            "weakMatches": weak_matches,
            "missingSkills": missing_skills,
        },
        "next_action": "rewrite",
    }


def generate_resume_rewrites(state: ApplicationAgentState) -> ApplicationAgentState:
    bullets = state["resume_profile"].get("bullets", [])
    matched_skills = [
        item["skill"]
        for item in state["match_result"].get("strongMatches", [])
    ]
    original = bullets[0] if bullets else "Built a software project."

    if matched_skills:
        skill_text = ", ".join(matched_skills[:4])
        suggested = f"{original.rstrip('.')} with emphasis on {skill_text} experience relevant to the target internship."
        needs_confirmation = False
    else:
        suggested = f"{original.rstrip('.')} with clearer scope, technical responsibility, and measurable outcome."
        needs_confirmation = True

    return {
        "rewrite_suggestions": [
            {
                "originalBullet": original,
                "suggestedBullet": suggested,
                "targetedSkills": matched_skills[:4],
                "evidenceSources": ["pasted_resume_text"],
                "unsupportedClaims": [],
                "confidence": 0.78 if matched_skills else 0.55,
                "needsUserConfirmation": needs_confirmation,
            }
        ],
        "next_action": "plan",
    }


def generate_learning_plan(state: ApplicationAgentState) -> ApplicationAgentState:
    missing = [
        item["skill"]
        for item in state["match_result"].get("missingSkills", [])
    ]
    focus_skills = missing or ["resume clarity", "project evidence", "interview explanation"]
    plan: list[dict] = []

    for day in range(1, 8):
        skill = focus_skills[(day - 1) % len(focus_skills)]
        plan.append(
            {
                "day": day,
                "title": f"Improve {skill}",
                "tasks": [
                    f"Study one practical example of {skill}.",
                    f"Apply {skill} to one resume or project detail.",
                    "Write one short note explaining what changed and why.",
                ],
                "targetSkills": [skill],
                "deliverable": f"One visible improvement related to {skill}.",
            }
        )

    return {
        "learning_plan": plan,
        "next_action": "done",
    }


def prepare_response(state: ApplicationAgentState) -> ApplicationAgentState:
    return {"next_action": "done"}


def _build_graph():
    graph = StateGraph(ApplicationAgentState)
    graph.add_node("validate_input", validate_input)
    graph.add_node("extract_job_requirements", extract_job_requirements)
    graph.add_node("extract_resume_profile", extract_resume_profile)
    graph.add_node("compare_skills", compare_skills)
    graph.add_node("generate_resume_rewrites", generate_resume_rewrites)
    graph.add_node("generate_learning_plan", generate_learning_plan)
    graph.add_node("prepare_response", prepare_response)

    graph.add_edge(START, "validate_input")
    graph.add_edge("validate_input", "extract_job_requirements")
    graph.add_edge("extract_job_requirements", "extract_resume_profile")
    graph.add_edge("extract_resume_profile", "compare_skills")
    graph.add_edge("compare_skills", "generate_resume_rewrites")
    graph.add_edge("generate_resume_rewrites", "generate_learning_plan")
    graph.add_edge("generate_learning_plan", "prepare_response")
    graph.add_edge("prepare_response", END)

    return graph.compile()


def _find_skills(text: str) -> list[str]:
    normalized = text.lower()
    found = []
    for skill in TECH_SKILLS:
        if skill.lower() in normalized:
            found.append(skill)
    return sorted(set(found))


def _extract_resume_bullets(text: str) -> list[str]:
    lines = [line.strip(" -•\t") for line in text.splitlines()]
    return [line for line in lines if len(line) >= 12]


def _skill_item(skill: str, status: str, evidence_text: str) -> dict:
    return {
        "skill": skill,
        "status": status,
        "evidence": [
            {
                "source": "pasted_text",
                "text": evidence_text,
            }
        ],
        "confidence": 0.9 if status == "matched" else 0.72,
    }


_compiled_graph = _build_graph()

