package com.internpilot.backend.domain;

import java.util.List;
import java.util.Map;

public record ApplicationAnalysisResponse(
        String applicationId,
        String analysisId,
        String status,
        Integer matchScore,
        Map<String, Object> scoreBreakdown,
        List<Map<String, Object>> strongMatches,
        List<Map<String, Object>> weakMatches,
        List<Map<String, Object>> missingSkills,
        List<Map<String, Object>> learningPlan,
        List<RewriteSuggestionView> rewriteSuggestions,
        List<String> warnings
) {
}

