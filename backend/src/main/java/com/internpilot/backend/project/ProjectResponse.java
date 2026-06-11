package com.internpilot.backend.project;

import java.time.Instant;
import java.util.List;

public record ProjectResponse(
        String id,
        String resumeId,
        String name,
        String description,
        List<String> techStack,
        String evidenceText,
        Instant createdAt,
        Instant updatedAt
) {
}

