package com.internpilot.backend.resume;

import java.time.Instant;

public record ResumeResponse(
        String id,
        String title,
        String rawText,
        String sourceType,
        boolean active,
        Instant createdAt,
        Instant updatedAt
) {
    static ResumeResponse fromEntity(ResumeEntity entity) {
        return new ResumeResponse(
                entity.getId(),
                entity.getTitle(),
                entity.getRawText(),
                entity.getSourceType(),
                entity.isActive(),
                entity.getCreatedAt(),
                entity.getUpdatedAt()
        );
    }
}

