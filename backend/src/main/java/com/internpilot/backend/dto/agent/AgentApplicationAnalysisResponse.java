package com.internpilot.backend.dto.agent;

import com.internpilot.backend.dto.LearningPlanDTO;
import com.internpilot.backend.dto.SkillMatchDTO;
import java.util.List;
import java.util.Map;

public record AgentApplicationAnalysisResponse(
        String runId,
        Integer matchScore,
        Map<String, Integer> scoreBreakdown,
        List<SkillMatchDTO> strongMatches,
        List<SkillMatchDTO> weakMatches,
        List<SkillMatchDTO> missingSkills,
        List<LearningPlanDTO> learningPlan,
        List<AgentRewriteSuggestionDTO> rewriteSuggestions,
        List<String> warnings,
        Map<String, Object> metadata
) {
}

