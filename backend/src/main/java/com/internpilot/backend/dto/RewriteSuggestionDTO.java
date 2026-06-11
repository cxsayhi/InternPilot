package com.internpilot.backend.dto;

import java.util.List;

public record RewriteSuggestionDTO(
        String id,
        String status,
        String originalBullet,
        String suggestedBullet,
        List<String> targetedSkills,
        List<String> evidenceSources,
        List<String> unsupportedClaims,
        Double confidence,
        Boolean needsUserConfirmation
) {
}

