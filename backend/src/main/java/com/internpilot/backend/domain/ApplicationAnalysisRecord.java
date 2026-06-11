package com.internpilot.backend.domain;

import com.internpilot.backend.dto.AnalyzeApplicationResponse;
import java.time.Instant;

public record ApplicationAnalysisRecord(
        String applicationId,
        String analysisId,
        String userId,
        String status,
        AnalyzeApplicationResponse response,
        String failureCode,
        Instant createdAt
) {
}
