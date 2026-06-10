package com.internpilot.backend.application;

import com.internpilot.backend.domain.AnalyzeApplicationRequest;
import com.internpilot.backend.domain.ApplicationAnalysisResponse;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/applications")
public class ApplicationAnalysisController {

    private final ApplicationAnalysisService analysisService;

    public ApplicationAnalysisController(ApplicationAnalysisService analysisService) {
        this.analysisService = analysisService;
    }

    @PostMapping("/analyze")
    public ResponseEntity<ApplicationAnalysisResponse> analyze(
            @Valid @RequestBody AnalyzeApplicationRequest request
    ) {
        String userId = "demo-user";
        return ResponseEntity.ok(analysisService.analyze(userId, request));
    }
}

