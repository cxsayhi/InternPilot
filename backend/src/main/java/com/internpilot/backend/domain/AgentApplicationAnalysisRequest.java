package com.internpilot.backend.domain;

public record AgentApplicationAnalysisRequest(
        String userId,
        String applicationId,
        String resumeText,
        String jobText,
        String company,
        String role
) {
}

