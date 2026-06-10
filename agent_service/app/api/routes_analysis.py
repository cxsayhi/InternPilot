from fastapi import APIRouter

from app.graphs.application_graph import run_application_graph
from app.schemas.analysis import ApplicationAnalysisRequest, ApplicationAnalysisResponse

router = APIRouter(prefix="/internal/agent", tags=["application-analysis"])


@router.post("/application-analysis", response_model=ApplicationAnalysisResponse)
def analyze_application(request: ApplicationAnalysisRequest) -> ApplicationAnalysisResponse:
    return run_application_graph(request)

