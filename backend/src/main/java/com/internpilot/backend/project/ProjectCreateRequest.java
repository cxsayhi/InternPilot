package com.internpilot.backend.project;

import jakarta.validation.constraints.NotBlank;
import java.util.List;

public record ProjectCreateRequest(
        String resumeId,
        @NotBlank String name,
        String description,
        List<String> techStack,
        String evidenceText
) {
}

