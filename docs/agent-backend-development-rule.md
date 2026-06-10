# InternPilot Backend Development Rule

## 1. Document Responsibility

This document defines the product backend rule for InternPilot.

It covers:

- frontend to Spring Boot to Agent Service call chain
- Spring Boot REST API ownership
- MySQL persistence ownership
- application analysis storage
- resume rewrite approval storage
- security, validation, and backend tests

It does not define LangGraph node internals, LangChain tools, prompt design, or LLM structured-output schemas. Those belong in `docs/langchain-ai-module-agent-development-rule.md`.

## 2. Backend Goal

The backend must turn one internship application analysis into durable product data.

For the MVP, the backend only needs to support this flow:

1. User pastes resume text.
2. User pastes job description text.
3. Frontend sends both texts to Spring Boot.
4. Spring Boot creates an application analysis request.
5. Spring Boot calls the Python Agent Service.
6. Agent Service returns structured analysis.
7. Spring Boot saves the analysis result.
8. Spring Boot saves resume rewrite suggestions as `PENDING_REVIEW`.
9. Frontend displays match result, missing skills, rewrite suggestions, and a 7-day action plan.
10. User can later approve, edit, or reject each rewrite suggestion.

Do not build PDF upload, vector search, dashboard statistics, history Q&A, interview generation, GitHub README analysis, or multi-agent orchestration in the MVP.

## 3. Fixed Service Ownership

Use three layers with fixed responsibilities:

```text
Vue3 Frontend
  -> Spring Boot Backend
    -> Python FastAPI Agent Service
      -> LLM provider
```

### Vue3 Frontend Owns

- text input UI for resume and job description
- submit action
- result rendering
- approval, edit, and reject UI for rewrite suggestions
- application list/detail screens for saved analyses

The frontend must never call the Python Agent Service directly.

### Spring Boot Backend Owns

- authentication and `user_id`
- public REST APIs
- request validation
- MySQL writes
- application status
- application analysis records
- rewrite suggestion review status
- approved resume content
- audit fields

Spring Boot is the only service allowed to persist product data in MySQL.

### Python Agent Service Owns

- job extraction
- resume extraction
- skill matching
- no-fabrication rewrite suggestion generation
- learning plan generation
- structured agent response

The Agent Service must not directly create MySQL product records in the MVP. It may keep run traces for execution debugging, but those are not product persistence. Durable LangGraph checkpoints are post-MVP.

## 4. Fixed Analyze Call Chain

The application analysis call chain is fixed:

```text
1. Vue3
   POST /api/applications/analyze
   Body: resumeText, jobText, optional company, optional role

2. Spring Boot
   - validates input
   - resolves user_id from auth
   - creates application row with status ANALYZING
   - calls Agent Service

3. Python Agent Service
   POST /internal/agent/application-analysis
   Body: userId, applicationId, resumeText, jobText, company, role
   Returns: structured analysis only

4. Spring Boot
   - saves application_analysis
   - saves rewrite suggestions as PENDING_REVIEW
   - saves skill_gap_events if present
   - updates application status to ANALYZED

5. Vue3
   receives saved application analysis response from Spring Boot
```

Required Spring Boot endpoint:

```http
POST /api/applications/analyze
```

Required Agent Service endpoint called by Spring Boot:

```http
POST /internal/agent/application-analysis
```

The frontend must not depend on Agent Service response shape. It depends on the Spring Boot response shape only.

## 5. Fixed Rewrite Approval Call Chain

Saving analysis and saving approved resume content are separate flows.

Analysis flow saves AI analysis and pending suggestions. It does not save approved resume content.

Approval flow is fixed:

```text
1. Vue3
   PATCH /api/resume-rewrite-suggestions/{suggestionId}/review
   Body: decision, editedBullet optional

2. Spring Boot
   - validates suggestion belongs to user
   - validates decision
   - if APPROVE: saves suggested bullet as approved resume content
   - if EDIT_AND_APPROVE: saves edited bullet as approved resume content
   - if REJECT: stores rejection status and optional feedback only

3. Vue3
   receives updated suggestion and approved content reference if created
```

Required Spring Boot endpoint:

```http
PATCH /api/resume-rewrite-suggestions/{suggestionId}/review
```

Allowed decisions:

- `APPROVE`
- `EDIT_AND_APPROVE`
- `REJECT`

The Agent Service is not called in the approval flow unless a later non-MVP validation endpoint is explicitly added.

## 6. Persistence Rule

Use MySQL as the source of truth for MVP product data.

Minimum MVP tables:

- `users`
- `applications`
- `application_analysis`
- `resume_rewrite_suggestions`
- `approved_resume_contents`
- `skill_gap_events`

Optional post-MVP tables:

- `resumes`
- `resume_versions`
- `projects`
- `application_notes`
- `agent_run_audit`

Minimum application statuses:

- `ANALYZING`
- `ANALYZED`
- `FAILED`
- `APPLIED`
- `REJECTED`

Minimum rewrite suggestion statuses:

- `PENDING_REVIEW`
- `APPROVED`
- `EDITED_AND_APPROVED`
- `REJECTED`

## 7. Analysis Vs Approved Content Rule

These two concepts must never be mixed.

### `application_analysis`

Stores what the agent said about one job application.

Allowed content:

- match score
- score breakdown
- strong matches
- weak matches
- missing skills
- learning plan
- generated rewrite suggestions snapshot
- warnings
- model metadata
- prompt version
- graph version

This table is analysis history. It is not a resume version.

### `resume_rewrite_suggestions`

Stores AI-generated suggestions for review.

Required fields:

- `id`
- `user_id`
- `application_id`
- `analysis_id`
- `original_bullet`
- `suggested_bullet`
- `targeted_skills`
- `evidence_sources`
- `unsupported_claims`
- `confidence`
- `status`
- `reviewed_at`

Suggestions start as `PENDING_REVIEW`.

### `approved_resume_contents`

Stores user-approved resume content only.

Rows may be created only when:

- user chooses `APPROVE`
- user chooses `EDIT_AND_APPROVE`

Rows must not be created during `/api/applications/analyze`.

## 8. Spring Boot API Contract

`POST /api/applications/analyze` request:

```json
{
  "resumeText": "string",
  "jobText": "string",
  "company": "string optional",
  "role": "string optional"
}
```

Response:

```json
{
  "applicationId": "app_123",
  "analysisId": "analysis_123",
  "status": "ANALYZED",
  "matchScore": 78,
  "scoreBreakdown": {},
  "strongMatches": [],
  "weakMatches": [],
  "missingSkills": [],
  "learningPlan": [],
  "rewriteSuggestions": [
    {
      "id": "sug_123",
      "status": "PENDING_REVIEW",
      "originalBullet": "Built an online shopping platform.",
      "suggestedBullet": "Developed Spring Boot REST APIs for product listing, cart management, and MySQL persistence.",
      "targetedSkills": ["Spring Boot", "REST API", "MySQL"],
      "evidenceSources": ["resume.project.online_shop"],
      "unsupportedClaims": [],
      "confidence": 0.86
    }
  ],
  "warnings": []
}
```

`PATCH /api/resume-rewrite-suggestions/{suggestionId}/review` request:

```json
{
  "decision": "EDIT_AND_APPROVE",
  "editedBullet": "Developed Spring Boot REST APIs for product listing, cart management, and MySQL persistence."
}
```

Response:

```json
{
  "suggestionId": "sug_123",
  "status": "EDITED_AND_APPROVED",
  "approvedContentId": "approved_123"
}
```

## 9. Agent Service Contract From Spring Boot

Spring Boot calls:

```http
POST /internal/agent/application-analysis
```

Request:

```json
{
  "userId": "user_123",
  "applicationId": "app_123",
  "resumeText": "string",
  "jobText": "string",
  "company": "string optional",
  "role": "string optional"
}
```

Response:

```json
{
  "runId": "run_123",
  "matchScore": 78,
  "scoreBreakdown": {},
  "strongMatches": [],
  "weakMatches": [],
  "missingSkills": [],
  "learningPlan": [],
  "rewriteSuggestions": [],
  "warnings": [],
  "metadata": {
    "model": "configured-in-agent-service",
    "graphVersion": "application_graph.v1",
    "promptVersions": {}
  }
}
```

Spring Boot must treat the Agent Service response as untrusted input and validate it before saving.

## 10. MVP Scope Rule

MVP includes only:

- paste resume text
- paste job description text
- analyze one application
- produce match score
- show strong matches, weak matches, and missing skills
- produce rewrite suggestions as `PENDING_REVIEW`
- produce a 7-day action plan
- save analysis history
- approve, edit-and-approve, or reject rewrite suggestions

MVP excludes:

- PDF upload
- Chroma, FAISS, or pgvector
- project retrieval
- application dashboard statistics
- history Q&A
- weekly planning automation
- interview question generator
- GitHub README analyzer
- multi-agent or deep-agent architecture
- automatic resume file export

## 11. Security And Privacy Rule

Resume and application data are personal data.

Backend requirements:

- Never log full resume text.
- Never log full job analysis payloads.
- Mask email, phone, address, and links where possible.
- Keep every query scoped by `user_id`.
- Validate request size for resume and job text.
- Store API keys only in environment variables.
- Add rate limits for LLM-heavy endpoints.
- Reject approval requests for suggestions not owned by the authenticated user.

## 12. Failure Handling Rule

If Agent Service fails:

1. Spring Boot stores application status as `FAILED`.
2. Spring Boot stores a sanitized error code and message.
3. Spring Boot returns a controlled error response to the frontend.
4. Spring Boot does not create rewrite suggestions.
5. Spring Boot does not create approved resume content.

Required error response:

```json
{
  "code": "AGENT_ANALYSIS_FAILED",
  "message": "Application analysis failed. Please try again later.",
  "retryable": true
}
```

## 13. Backend Testing Rule

Required MVP backend tests:

- `POST /api/applications/analyze` validates empty resume text.
- `POST /api/applications/analyze` validates empty job text.
- Spring Boot calls Agent Service with the fixed internal contract.
- successful analysis saves `application_analysis`.
- successful analysis saves suggestions as `PENDING_REVIEW`.
- successful analysis does not create `approved_resume_contents`.
- `APPROVE` creates `approved_resume_contents`.
- `EDIT_AND_APPROVE` creates `approved_resume_contents` using edited text.
- `REJECT` does not create `approved_resume_contents`.
- user cannot review another user's suggestion.
- Agent Service failure marks application as `FAILED`.

## 14. Definition Of Done

A backend feature is done only when:

- it follows the fixed Vue3 -> Spring Boot -> Agent Service call chain
- public APIs are owned by Spring Boot
- product persistence is owned by Spring Boot
- application analysis storage is separate from approved resume content storage
- rewrite suggestions start as `PENDING_REVIEW`
- approved resume content is created only by explicit user approval
- MVP exclusions are not accidentally implemented early
- tests cover the persistence distinction
