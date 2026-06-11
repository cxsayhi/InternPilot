package com.internpilot.backend.dto.agent;

public record AgentApplicationAnalysisRequest(
        String userId,
        String applicationId,
        String resumeText,
        String jobText,
        String company,
        String role
) {
}

