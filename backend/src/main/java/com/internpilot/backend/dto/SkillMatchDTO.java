package com.internpilot.backend.dto;

import java.util.List;

public record SkillMatchDTO(
        String skill,
        String status,
        List<SkillEvidenceDTO> evidence,
        Double confidence
) {
}

