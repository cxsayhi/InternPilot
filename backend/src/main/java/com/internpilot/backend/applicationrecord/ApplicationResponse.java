package com.internpilot.backend.applicationrecord;

import java.time.Instant;

public record ApplicationResponse(
        String id,
        String resumeId,
        String company,
        String role,
        String jobText,
        String status,
        Instant createdAt,
        Instant updatedAt
) {
    static ApplicationResponse fromEntity(ApplicationEntity entity) {
        return new ApplicationResponse(
                entity.getId(),
                entity.getResumeId(),
                entity.getCompany(),
                entity.getRole(),
                entity.getJobText(),
                entity.getStatus(),
                entity.getCreatedAt(),
                entity.getUpdatedAt()
        );
    }
}

