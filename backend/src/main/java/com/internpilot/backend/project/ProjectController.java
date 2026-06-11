package com.internpilot.backend.project;

import com.internpilot.backend.common.UserContext;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/projects")
public class ProjectController {

    private final ProjectService projectService;

    public ProjectController(ProjectService projectService) {
        this.projectService = projectService;
    }

    @PostMapping
    public ResponseEntity<ProjectResponse> create(
            @RequestHeader(value = UserContext.USER_ID_HEADER, defaultValue = UserContext.DEFAULT_USER_ID) String userId,
            @Valid @RequestBody ProjectCreateRequest request
    ) {
        return ResponseEntity.ok(projectService.create(userId, request));
    }

    @GetMapping
    public ResponseEntity<List<ProjectResponse>> list(
            @RequestHeader(value = UserContext.USER_ID_HEADER, defaultValue = UserContext.DEFAULT_USER_ID) String userId
    ) {
        return ResponseEntity.ok(projectService.list(userId));
    }
}

