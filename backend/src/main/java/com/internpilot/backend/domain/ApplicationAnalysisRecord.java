package com.internpilot.backend.domain;

import java.time.Instant;

public record ApplicationAnalysisRecord(
        String applicationId,
        String analysisId,
        String userId,
        String status,
        ApplicationAnalysisResponse response,
        String failureCode,
        Instant createdAt
) {
}

