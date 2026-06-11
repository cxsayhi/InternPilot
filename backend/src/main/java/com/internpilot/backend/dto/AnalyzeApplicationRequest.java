package com.internpilot.backend.dto;

import jakarta.validation.constraints.NotBlank;

public record AnalyzeApplicationRequest(
        @NotBlank String resumeText,
        @NotBlank String jobText,
        String company,
        String role
) {
}

