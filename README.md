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

