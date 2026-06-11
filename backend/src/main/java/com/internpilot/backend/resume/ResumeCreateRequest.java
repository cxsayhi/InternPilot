package com.internpilot.backend.resume;

import jakarta.validation.constraints.NotBlank;

public record ResumeCreateRequest(
        @NotBlank String title,
        @NotBlank String rawText,
        String sourceType
) {
}

