from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.schemas.run import AgentError, LLM_OUTPUT_VALIDATION_FAILED


ModelT = TypeVar("ModelT", bound=BaseModel)
RepairFn = Callable[[Any, ValidationError], Any]


class StructuredOutputValidationError(Exception):
    def __init__(self, error: AgentError, validation_error: ValidationError):
        super().__init__(error.message)
        self.error = error
        self.validation_error = validation_error


def validate_structured_output(
    model_type: type[ModelT],
    payload: Any,
    repair_fn: RepairFn | None = None,
) -> ModelT:
    try:
        return model_type.model_validate(payload)
    except ValidationError as first_error:
        if repair_fn is not None:
            try:
                repaired_payload = repair_fn(payload, first_error)
                return model_type.model_validate(repaired_payload)
            except ValidationError as second_error:
                raise _validation_failure(model_type, second_error) from second_error
            except Exception as repair_error:
                raise _validation_failure(model_type, first_error) from repair_error

        raise _validation_failure(model_type, first_error) from first_error


def _validation_failure(
    model_type: type[BaseModel],
    validation_error: ValidationError,
) -> StructuredOutputValidationError:
    error = AgentError(
        code=LLM_OUTPUT_VALIDATION_FAILED,
        message=f"Structured output failed validation for {model_type.__name__}.",
        retryable=False,
    )
    return StructuredOutputValidationError(error, validation_error)
