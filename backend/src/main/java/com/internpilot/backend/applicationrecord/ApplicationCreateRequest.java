package com.internpilot.backend.applicationrecord;

import jakarta.validation.constraints.NotBlank;

public record ApplicationCreateRequest(
        String resumeId,
        String company,
        String role,
        @NotBlank String jobText
) {
}

