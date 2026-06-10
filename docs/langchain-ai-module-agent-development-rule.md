# InternPilot LangChain AI Module Agent Development Rule

## 1. Module Purpose

The LangChain AI module is the reasoning engine for InternPilot. It should convert pasted resume text and job descriptions into structured analysis that the Spring Boot backend can persist and display.

The module must not behave like a free-form chatbot. It must behave like a typed, observable, stateful agent workflow.

This document defines only the Python FastAPI Agent Service internals. Spring Boot API design, MySQL product persistence, and frontend call flow are defined in `docs/agent-backend-development-rule.md`.

Primary responsibilities:

1. Extract job requirements.
2. Extract resume evidence from pasted resume text.
3. Compare user evidence with job requirements.
4. Generate no-fabrication resume rewrite suggestions.
5. Generate a practical improvement plan.
6. Produce structured outputs for Spring Boot.

Post-MVP responsibilities:

- retrieve relevant stored projects
- answer history queries
- use durable LangGraph checkpoints
- add human-in-the-loop interrupts for sensitive tools

## 2. Framework Rule

Use LangChain for:

- model initialization
- tool definitions
- structured output parsing
- prompt composition
- simple tool-calling agents when needed

Use LangGraph for:

- the main application-analysis workflow
- durable graph state
- explicit node orchestration
- replay/debugging during development
- post-MVP checkpointing by thread
- post-MVP human-in-the-loop interrupts
- post-MVP long-running or resumable runs

Do not implement the main analysis as one `agent.invoke()` call with a giant prompt. Use a LangGraph state machine with explicit nodes.

## 3. Package Boundary Rule

Keep the AI module independent from Spring Boot, frontend code, and database-specific controller logic.

Recommended MVP Python package layout:

```text
agent_service/
  app/
    main.py
    api/
      routes_analysis.py
      routes_runs.py
    core/
      config.py
      logging.py
      errors.py
      model_factory.py
    schemas/
      job.py
      resume.py
      project.py
      match.py
      rewrite.py
      plan.py
      run.py
    prompts/
      job_extraction.md
      resume_extraction.md
      resume_rewrite.md
      learning_plan.md
    tools/
      job_tools.py
      resume_tools.py
      matching_tools.py
      rewrite_tools.py
      plan_tools.py
    graphs/
      application_graph.py
      state.py
      nodes.py
      edges.py
    services/
      analysis_service.py
      run_service.py
    tests/
      fixtures/
      unit/
      integration/
```

FastAPI routes may call the graph. Graph nodes may call tools and internal services. Tools must not import FastAPI route objects.

Post-MVP folders such as `retrieval/`, `memory/`, and `routes_history.py` may be added only after the MVP graph is stable.

## 4. State Rule

The graph state is the contract between nodes. Keep it typed and stable.

Use `TypedDict` for graph state and Pydantic models for request, response, and LLM structured output schemas.

Required graph state:

```python
from typing import TypedDict, Literal

class ApplicationAgentState(TypedDict, total=False):
    run_id: str
    user_id: str
    resume_id: str | None
    application_id: str | None

    resume_text: str
    job_text: str

    job_profile: dict
    resume_profile: dict
    match_result: dict
    rewrite_suggestions: list[dict]
    learning_plan: list[dict]

    warnings: list[str]
    errors: list[str]
    next_action: Literal[
        "extract_job",
        "extract_resume",
        "match",
        "rewrite",
        "plan",
        "done",
        "failed",
    ]
```

Rules:

- Every node must return a partial state update.
- Nodes must not mutate shared dictionaries in place.
- State fields passed to the backend must be JSON-serializable.
- Large raw text should be stored once and referenced by ID when possible.
- Do not place API keys, provider clients, or database sessions in graph state.
- In MVP, `application_id` is a Spring Boot identifier passed through for traceability only.

## 5. Graph Rule

The MVP graph must be deterministic in structure and agentic only where it adds value.

Required node sequence:

```text
START
  -> validate_input
  -> extract_job_requirements
  -> extract_resume_profile
  -> compare_skills
  -> generate_resume_rewrites
  -> generate_learning_plan
  -> prepare_response
  -> END
```

Rules:

- Extraction, matching, rewrite, and planning must be separate nodes.
- Matching should be deterministic where possible and LLM-assisted only for explanation.
- A failed node should add a structured error to state and route to `failed_response`.
- Do not let the LLM decide whether to save or overwrite user resume data.
- The graph returns analysis only. It does not save approved resume content.
- Durable checkpointing and approval interrupts are post-MVP features.

## 6. Tool Rule

Tools must be narrow, typed, and auditable.

Every tool must have:

- type hints
- a concise docstring
- Pydantic input/output models when the shape is complex
- no hidden writes unless the tool name clearly says `save`, `update`, or `delete`
- predictable errors

Good tool names:

- `extract_job_requirements`
- `extract_resume_profile`
- `calculate_skill_match`
- `generate_rewrite_candidates`
- `generate_learning_plan`

Bad tool names:

- `process_everything`
- `ask_ai`
- `do_resume`
- `handle_application`
- `save_stuff`

Tool output must include evidence. Example:

```json
{
  "skill": "Spring Boot",
  "status": "matched",
  "evidence": [
    {
      "source": "resume.project.online_shop",
      "text": "Built REST APIs with Spring Boot and MyBatis"
    }
  ],
  "confidence": 0.91
}
```

## 7. Structured Output Rule

All LLM calls that feed product logic must return structured data.

Use Pydantic schemas for:

- job extraction
- resume extraction
- rewrite suggestions
- learning plans

Required behavior:

- Validate every LLM response.
- Retry once with a repair prompt if validation fails.
- Return a controlled `LLM_OUTPUT_VALIDATION_FAILED` error if repair fails.
- Keep user-facing prose separate from machine-readable data.

Example schema:

```python
from pydantic import BaseModel, Field

class ExtractedSkill(BaseModel):
    name: str
    category: str
    importance: str = Field(pattern="^(required|preferred|bonus)$")
    evidence_text: str | None = None

class JobProfile(BaseModel):
    role_title: str | None
    company: str | None
    required_skills: list[ExtractedSkill]
    preferred_skills: list[ExtractedSkill]
    responsibilities: list[str]
    keywords: list[str]
```

## 8. Prompt Rule

Prompts are source code. Keep them versioned, reviewed, and tested.

Every prompt must include:

- purpose
- input fields
- output schema
- no-fabrication instruction
- evidence requirement
- refusal or uncertainty behavior

Prompt files must not include API keys, local machine paths, or user-specific private data.

Prompt version must be included in every graph run result:

```json
{
  "promptVersions": {
    "jobExtraction": "job_extraction.v1",
    "resumeRewrite": "resume_rewrite.v1"
  }
}
```

## 9. No-Fabrication Rule

The AI module must never invent resume content.

A rewrite suggestion is valid only when it is supported by at least one evidence source:

- original resume bullet
- parsed project record
- approved user profile field
- explicit user-provided clarification

In the MVP, the only required evidence source is pasted resume text. Parsed project records and approved user profile fields are post-MVP inputs that Spring Boot may provide later.

Each rewrite suggestion must include:

```json
{
  "originalBullet": "Built an online shopping platform.",
  "rewrittenBullet": "Developed Spring Boot REST APIs for product listing, cart management, and MySQL persistence.",
  "targetedSkills": ["Spring Boot", "REST API", "MySQL"],
  "evidenceSources": ["resume.project.online_shopping_platform"],
  "unsupportedClaims": [],
  "confidence": 0.86,
  "needsUserConfirmation": false
}
```

If the user lacks evidence for a target skill, generate an action-plan item instead of a fake bullet.

## 10. Matching Rule

Skill matching must be explainable and partly deterministic.

Recommended scoring:

- required skill coverage: 40
- preferred skill coverage: 15
- resume evidence strength: 20
- responsibility alignment: 15
- resume keyword clarity: 10

The score must include a breakdown:

```json
{
  "score": 78,
  "breakdown": {
    "requiredSkillCoverage": 32,
    "preferredSkillCoverage": 8,
    "resumeEvidenceStrength": 17,
    "responsibilityAlignment": 13,
    "resumeKeywordClarity": 8
  },
  "strongMatches": [],
  "weakMatches": [],
  "missingSkills": []
}
```

Do not accept an LLM-generated score unless the module can explain it with matched and missing evidence.

## 11. Retrieval Rule

Retrieval is post-MVP.

Retrieval should support the agent, not replace structured user data.

Use vector retrieval for:

- finding relevant projects
- finding similar past applications
- retrieving approved resume bullets
- finding repeated missing skills

Use relational data for:

- user identity
- application status
- approved resume versions
- project metadata
- audit history

Rules:

- Store chunk metadata: `user_id`, `source_type`, `source_id`, `created_at`, `visibility`, `approved`.
- Filter retrieval by `user_id`.
- Never retrieve another user's data.
- Return source IDs with every retrieved chunk.
- Do not use unapproved rewrite suggestions as resume evidence.
- Do not add Chroma, FAISS, pgvector, or project retrieval to the MVP.

## 12. Memory Rule

Memory is post-MVP except for lightweight run tracing.

Eventually use two kinds of memory:

- thread memory: current analysis conversation and graph checkpoint state
- user memory: durable profile, projects, skills, applications, and approved bullets

Thread memory must use a LangGraph checkpointer with a stable `thread_id`.

User memory must be stored outside the checkpoint, in product storage or a dedicated long-term store.

The graph may read user memory when Spring Boot provides it, but it must not silently rewrite user memory. Product memory writes belong to Spring Boot.

## 13. Human-In-The-Loop Rule

Human approval is handled by Spring Boot in the MVP.

The Agent Service generates rewrite suggestions only. It must not mark suggestions as approved and must not create approved resume content.

LangGraph human-in-the-loop interrupts are post-MVP and may be used later for sensitive Agent Service tools.

Require approval for:

- saving approved resume rewrites
- marking a suggested bullet as final
- updating canonical user skills
- updating project descriptions
- sending or exporting application material

Approval decision types:

- `approve`
- `edit`
- `reject`

Rules:

- `approve` saves exactly the proposed content.
- `edit` saves the user's edited content and marks it as user-approved.
- `reject` stores rejection feedback but does not save the rewrite as approved.
- Application analysis history may be saved as analysis, but not as approved resume content.
- In MVP, these decisions are implemented in Spring Boot, not inside the Agent Service graph.

## 14. Model Configuration Rule

Model choice must be centralized in `model_factory.py`.

Required configuration:

- model provider
- model name
- temperature
- max tokens
- timeout
- retry count
- structured output strategy
- tracing flag

Recommended defaults:

- extraction temperature: `0.0`
- matching explanation temperature: `0.1`
- rewrite temperature: `0.2`
- learning plan temperature: `0.2`

Never hardcode model names inside graph nodes or tools.

## 15. Error Handling Rule

Every Agent Service error returned to Spring Boot must have a stable code.

Required error codes:

- `INVALID_INPUT`
- `RESUME_TEXT_EMPTY`
- `JOB_TEXT_EMPTY`
- `LLM_TIMEOUT`
- `LLM_OUTPUT_VALIDATION_FAILED`
- `INTERNAL_AGENT_ERROR`

Post-MVP error codes:

- `RETRIEVAL_FAILED`
- `CHECKPOINT_FAILED`
- `HUMAN_APPROVAL_REQUIRED`
- `UNAUTHORIZED_MEMORY_ACCESS`

Errors returned to the backend must include:

```json
{
  "code": "LLM_OUTPUT_VALIDATION_FAILED",
  "message": "The model returned data that did not match the expected schema.",
  "retryable": true,
  "runId": "run_123"
}
```

Do not expose full prompts, raw resume text, provider stack traces, or API keys in error responses.

## 16. Observability Rule

Every graph run must be traceable.

Log:

- `run_id`
- `user_id`
- `application_id`
- graph version
- prompt versions
- model name
- node start/end
- latency per node
- token usage when available
- structured error codes

Log `thread_id` only after durable checkpointing is added post-MVP.

Do not log:

- full resume text
- full job text
- phone numbers
- email addresses
- addresses
- API keys

Use tracing in development to inspect tool calls, node transitions, and structured output failures.

## 17. Internal API Response Rule

The AI module response must be stable enough for Spring Boot validation and persistence.

Spring Boot calls this internal Agent Service endpoint:

```http
POST /internal/agent/application-analysis
```

Response shape:

```json
{
  "runId": "run_123",
  "matchScore": 78,
  "scoreBreakdown": {},
  "strongMatches": [],
  "weakMatches": [],
  "missingSkills": [],
  "rewriteSuggestions": [],
  "learningPlan": [],
  "warnings": [],
  "metadata": {
    "graphVersion": "application_graph.v1",
    "model": "configured-in-model-factory",
    "promptVersions": {}
  }
}
```

The Agent Service must not return approved resume content. It returns suggestions only; Spring Boot stores them as `PENDING_REVIEW`.

## 18. Testing Rule

The AI module must have deterministic tests around the graph and tools.

Required unit tests:

- job extraction schema validation
- resume extraction schema validation
- deterministic skill matching
- no-fabrication rewrite validation
- unsupported claims detection
- learning plan length and skill coverage
- error response formatting

Required graph tests:

- happy path analysis run
- empty resume input
- empty job input
- malformed LLM output then repair success
- malformed LLM output then controlled failure
- graph returns suggestions without approving or saving them

LLM provider integration tests should be separate from normal CI and guarded by environment variables.

## 19. MVP Rule

Build the module in this order:

1. Pydantic schemas.
2. Deterministic matching logic.
3. Prompt files.
4. LLM extraction with structured output.
5. LangGraph MVP workflow.
6. Rewrite generation with no-fabrication validation.
7. 3-day learning plan generation.
8. FastAPI endpoint.

MVP explicitly excludes:

- project retrieval
- vector DB
- checkpoint persistence
- human approval branch inside Agent Service
- history query workflow
- subagents

Do not add subagents until the single graph produces reliable, tested, structured results.

## 20. Deep Agent Extension Rule

Only add deep-agent or multi-agent behavior after the MVP graph is stable.

Allowed future subagents:

- `JobAnalysisAgent`
- `ResumeCriticAgent`
- `SkillGapPlannerAgent`
- `ApplicationTrackerAgent`

Subagents must return structured outputs into the parent graph state. They must not write directly to durable storage.

## 21. Definition Of Done

A LangChain AI module feature is done only when:

- It has typed schemas.
- It has a graph node or tool with one clear responsibility.
- It validates LLM output.
- It provides evidence for claims.
- It avoids unsupported resume claims.
- It produces Spring-Boot-ready structured data.
- It includes tests with realistic student resume and internship fixtures.
- It can be traced by `run_id`.
- It can be resumed by `thread_id` only after checkpointing is added post-MVP.

## 22. Official References

- LangChain Python overview: https://docs.langchain.com/oss/python/langchain/overview
- LangGraph Python overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangChain structured output: https://docs.langchain.com/oss/python/langchain/structured-output
- LangChain tools: https://docs.langchain.com/oss/python/langchain/tools
- LangChain human-in-the-loop: https://docs.langchain.com/oss/python/langchain/human-in-the-loop
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
