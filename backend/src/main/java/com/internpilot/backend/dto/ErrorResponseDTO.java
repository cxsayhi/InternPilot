package com.internpilot.backend.dto;

public record ErrorResponseDTO(
        String code,
        String message,
        boolean retryable,
        String traceId
) {
}

