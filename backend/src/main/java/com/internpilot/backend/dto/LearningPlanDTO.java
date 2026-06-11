package com.internpilot.backend.dto;

import java.util.List;

public record LearningPlanDTO(
        Integer day,
        String title,
        List<String> tasks,
        List<String> targetSkills,
        String deliverable
) {
}

