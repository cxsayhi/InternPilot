package com.internpilot.backend.domain;

import java.util.List;
import java.util.Map;

public record AgentApplicationAnalysisResponse(
        String runId,
        Integer matchScore,
        Map<String, Object> scoreBreakdown,
        List<Map<String, Object>> strongMatches,
        List<Map<String, Object>> weakMatches,
        List<Map<String, Object>> missingSkills,
        List<Map<String, Object>> learningPlan,
        List<AgentRewriteSuggestion> rewriteSuggestions,
        List<String> warnings,
        Map<String, Object> metadata
) {
}

