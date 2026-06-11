package com.internpilot.backend.resume;

import com.internpilot.backend.common.UserContext;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/resumes")
public class ResumeController {

    private final ResumeService resumeService;

    public ResumeController(ResumeService resumeService) {
        this.resumeService = resumeService;
    }

    @PostMapping
    public ResponseEntity<ResumeResponse> create(
            @RequestHeader(value = UserContext.USER_ID_HEADER, defaultValue = UserContext.DEFAULT_USER_ID) String userId,
            @Valid @RequestBody ResumeCreateRequest request
    ) {
        return ResponseEntity.ok(resumeService.create(userId, request));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ResumeResponse> getById(
            @RequestHeader(value = UserContext.USER_ID_HEADER, defaultValue = UserContext.DEFAULT_USER_ID) String userId,
            @PathVariable String id
    ) {
        return ResponseEntity.ok(resumeService.getById(userId, id));
    }
}

