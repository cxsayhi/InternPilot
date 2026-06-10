from fastapi import FastAPI

from app.api.routes_analysis import router as analysis_router

app = FastAPI(
    title="InternPilot Agent Service",
    version="0.1.0",
    description="Internal FastAPI service for internship application analysis.",
)

app.include_router(analysis_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

