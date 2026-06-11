from fastapi import APIRouter, HTTPException

from app.graphs.application_graph import run_application_graph
from app.schemas.run import AnalyzeApplicationRequest, AnalyzeApplicationResponse
from app.services.structured_output import StructuredOutputValidationError

router = APIRouter(prefix="/internal/agent", tags=["application-analysis"])


@router.post("/application-analysis", response_model=AnalyzeApplicationResponse)
def analyze_application(request: AnalyzeApplicationRequest) -> AnalyzeApplicationResponse:
    try:
        return run_application_graph(request)
    except StructuredOutputValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.error.model_dump()) from exc
