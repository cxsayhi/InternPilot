from __future__ import annotations

from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from app.core.config import settings
from app.graphs.state import ApplicationAgentState
from app.schemas.job import JobProfile
from app.schemas.match import MatchResult
from app.schemas.plan import LearningPlanItem
from app.schemas.project import ProjectEvidence
from app.schemas.resume import ResumeProfile
from app.schemas.rewrite import RewriteSuggestion
from app.schemas.run import (
    AgentMetadata,
    AnalyzeApplicationRequest,
    AnalyzeApplicationResponse,
)
from app.services.job_extraction import (
    JOB_EXTRACTION_PROMPT_VERSION,
    extract_job_profile,
)
from app.services.skill_matching import (
    calculate_skill_match,
    find_known_skills,
    is_skill_inventory_line,
    is_preferred_skill_line,
)
from app.services.structured_output import validate_structured_output


def run_application_graph(request: AnalyzeApplicationRequest) -> AnalyzeApplicationResponse:
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
    match_result = validate_structured_output(MatchResult, final_state["match_result"])

    return validate_structured_output(
        AnalyzeApplicationResponse,
        {
            "runId": final_state["run_id"],
            "matchScore": match_result.score,
            "scoreBreakdown": match_result.breakdown,
            "strongMatches": match_result.strongMatches,
            "weakMatches": match_result.weakMatches,
            "missingSkills": match_result.missingSkills,
            "rewriteSuggestions": final_state.get("rewrite_suggestions", []),
            "learningPlan": final_state.get("learning_plan", []),
            "warnings": final_state.get("warnings", []),
            "metadata": AgentMetadata(
                graphVersion=settings.graph_version,
                model=settings.model_name,
                promptVersions={
                    "jobExtraction": _job_extraction_prompt_version(),
                    "resumeExtraction": "deterministic_mvp.v1",
                    "rewrite": "deterministic_mvp.v1",
                    "learningPlan": "deterministic_mvp.v1",
                },
            ),
        },
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

    if settings.job_extraction_mode == "llm":
        extracted_profile = extract_job_profile(job_text)
        job_profile = extracted_profile.model_copy(
            update={
                "company": state.get("company") or extracted_profile.company,
                "role_title": state.get("role") or extracted_profile.role_title,
            }
        )
        return {
            "job_profile": job_profile.model_dump(),
            "next_action": "extract_resume",
        }

    required_skills, preferred_skills = _split_required_and_preferred_skills(job_text)
    job_profile = validate_structured_output(
        JobProfile,
        {
            "company": state.get("company"),
            "role_title": state.get("role"),
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "responsibilities": _extract_responsibilities(job_text),
            "keywords": [*required_skills, *preferred_skills],
        },
    )
    return {
        "job_profile": job_profile.model_dump(),
        "next_action": "extract_resume",
    }


def extract_resume_profile(state: ApplicationAgentState) -> ApplicationAgentState:
    resume_text = state["resume_text"]
    skills = _find_skills(resume_text)
    bullets = _extract_resume_bullets(resume_text)
    projects = _extract_project_evidence(bullets)
    resume_profile = validate_structured_output(
        ResumeProfile,
        {
            "skills": skills,
            "bullets": bullets,
            "projects": projects,
        },
    )
    return {
        "resume_profile": resume_profile.model_dump(),
        "next_action": "match",
    }


def compare_skills(state: ApplicationAgentState) -> ApplicationAgentState:
    job_profile = validate_structured_output(JobProfile, state["job_profile"])
    resume_profile = validate_structured_output(ResumeProfile, state["resume_profile"])
    projects = [
        validate_structured_output(ProjectEvidence, project)
        for project in resume_profile.projects
    ]
    match_result = calculate_skill_match(
        job_profile=job_profile,
        resume_profile=resume_profile,
        projects=projects,
    )

    return {
        "match_result": match_result.model_dump(),
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

    suggestion = validate_structured_output(
        RewriteSuggestion,
        {
            "originalBullet": original,
            "suggestedBullet": suggested,
            "targetedSkills": matched_skills[:4],
            "evidenceSources": ["pasted_resume_text"],
            "unsupportedClaims": [],
            "confidence": 0.78 if matched_skills else 0.55,
            "needsUserConfirmation": needs_confirmation,
        },
    )

    return {
        "rewrite_suggestions": [suggestion.model_dump()],
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
        plan_item = validate_structured_output(
            LearningPlanItem,
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
            },
        )
        plan.append(plan_item.model_dump())

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
    return find_known_skills(text)


def _job_extraction_prompt_version() -> str:
    if settings.job_extraction_mode == "llm":
        return JOB_EXTRACTION_PROMPT_VERSION
    return "deterministic_mvp.v1"


def _split_required_and_preferred_skills(text: str) -> tuple[list[str], list[str]]:
    required: list[str] = []
    preferred: list[str] = []

    for line in _clean_lines(text):
        line_skills = _find_skills(line)
        if not line_skills:
            continue
        if is_preferred_skill_line(line):
            preferred.extend(line_skills)
        else:
            required.extend(line_skills)

    all_skills = _find_skills(text)
    assigned = set(required) | set(preferred)
    required.extend(skill for skill in all_skills if skill not in assigned)
    preferred = [skill for skill in preferred if skill not in set(required)]

    return sorted(set(required)), sorted(set(preferred))


def _extract_responsibilities(text: str) -> list[str]:
    return [
        line
        for line in _clean_lines(text)
        if len(line) >= 12 and not line.lower().strip(":").endswith("requirements")
    ]


def _extract_resume_bullets(text: str) -> list[str]:
    lines = [line.strip(" -•\t") for line in text.splitlines()]
    return [line for line in lines if len(line) >= 12]


def _extract_project_evidence(bullets: list[str]) -> list[dict]:
    projects: list[dict] = []
    for index, bullet in enumerate(bullets, start=1):
        if is_skill_inventory_line(bullet):
            continue
        tech_stack = _find_skills(bullet)
        if not tech_stack:
            continue
        project = validate_structured_output(
            ProjectEvidence,
            {
                "name": f"Resume bullet {index}",
                "techStack": tech_stack,
                "evidenceText": bullet,
                "source": "pasted_resume_text",
            },
        )
        projects.append(project.model_dump())
    return projects


def _clean_lines(text: str) -> list[str]:
    return [
        line.strip(" -•\t")
        for line in text.splitlines()
        if line.strip(" -•\t")
    ]


_compiled_graph = _build_graph()
