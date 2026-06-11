package com.internpilot.backend.dto.agent;

import java.util.List;

public record AgentRewriteSuggestionDTO(
        String originalBullet,
        String suggestedBullet,
        List<String> targetedSkills,
        List<String> evidenceSources,
        List<String> unsupportedClaims,
        Double confidence,
        Boolean needsUserConfirmation
) {
}

