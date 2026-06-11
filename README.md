# InternPilot

InternPilot is an AI internship application agent. The MVP focuses on one core chain:

```text
User pastes/uploads resume + pastes job JD
  -> system analyzes match quality
  -> outputs strong matches, weak matches, and missing skills
  -> generates resume bullet rewrite suggestions
  -> generates a 7-day improvement plan
  -> saves the analysis record
```

## Architecture

The service boundary is fixed:

```text
Frontend
  -> Spring Boot Backend
    -> Python FastAPI Agent Service
```

The frontend must never call the Python Agent Service directly.

## Project Layout

```text
internpilot/
  backend/              # Spring Boot public API and product persistence
  agent_service/        # Python FastAPI + LangChain/LangGraph reasoning service
  frontend/             # Vue3 application
  docs/                 # development rules and architecture notes
  docker-compose.yml
```

## Phase 1 Scope

Phase 1 creates the project skeleton only:

- Spring Boot backend skeleton
- Python FastAPI Agent Service skeleton
- Vue3 frontend skeleton
- Docker Compose skeleton
- fixed `Frontend -> Spring Boot -> Agent Service` call chain

The current backend stores analysis records in memory as a temporary Phase 1 placeholder. MySQL persistence will be implemented in a later phase.

## Database Schema

The MVP MySQL schema lives at:

```text
backend/src/main/resources/db/migration/V1__create_mvp_schema.sql
```

It defines only the Phase 2 minimum tables:

- `users`
- `resumes`
- `projects`
- `applications`
- `application_analysis`
- `resume_rewrite_suggestions`

## Phase 3 Business APIs

Phase 3 adds ordinary Spring Boot business APIs without LLM calls:

```http
POST /api/resumes
GET  /api/resumes/{id}

POST /api/projects
GET  /api/projects

POST /api/applications
GET  /api/applications
GET  /api/applications/{id}
```

During MVP development, requests use the `X-User-Id` header for user isolation. If the header is missing, the backend uses `demo-user`.

All resource reads are scoped by `user_id`; the backend must never read resumes, projects, or applications by ID alone.

## Local Development

Backend:

```bash
cd backend
mvn spring-boot:run
```

Agent Service:

```bash
cd agent_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Docker Compose:

```bash
docker compose up --build
```

Default local ports:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8080`
- Agent Service: `http://localhost:8000`
