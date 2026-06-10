package com.internpilot.backend.domain;

import java.util.List;

public record AgentRewriteSuggestion(
        String originalBullet,
        String suggestedBullet,
        List<String> targetedSkills,
        List<String> evidenceSources,
        List<String> unsupportedClaims,
        Double confidence,
        Boolean needsUserConfirmation
) {
}

