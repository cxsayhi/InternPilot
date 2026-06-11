package com.internpilot.backend.dto;

import java.util.List;

public record AnalyzeApplicationResponse(
        String applicationId,
        String analysisId,
        String status,
        MatchResultDTO matchResult,
        List<RewriteSuggestionDTO> rewriteSuggestions,
        List<LearningPlanDTO> learningPlan,
        List<String> warnings
) {
}

