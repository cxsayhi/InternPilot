package com.internpilot.backend.dto;

import java.util.List;
import java.util.Map;

public record MatchResultDTO(
        Integer score,
        Map<String, Integer> scoreBreakdown,
        List<SkillMatchDTO> strongMatches,
        List<SkillMatchDTO> weakMatches,
        List<SkillMatchDTO> missingSkills
) {
}

