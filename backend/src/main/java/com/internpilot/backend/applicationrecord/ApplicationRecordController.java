package com.internpilot.backend.applicationrecord;

import com.internpilot.backend.common.UserContext;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/applications")
public class ApplicationRecordController {

    private final ApplicationRecordService applicationRecordService;

    public ApplicationRecordController(ApplicationRecordService applicationRecordService) {
        this.applicationRecordService = applicationRecordService;
    }

    @PostMapping
    public ResponseEntity<ApplicationResponse> create(
            @RequestHeader(value = UserContext.USER_ID_HEADER, defaultValue = UserContext.DEFAULT_USER_ID) String userId,
            @Valid @RequestBody ApplicationCreateRequest request
    ) {
        return ResponseEntity.ok(applicationRecordService.create(userId, request));
    }

    @GetMapping
    public ResponseEntity<List<ApplicationResponse>> list(
            @RequestHeader(value = UserContext.USER_ID_HEADER, defaultValue = UserContext.DEFAULT_USER_ID) String userId
    ) {
        return ResponseEntity.ok(applicationRecordService.list(userId));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApplicationResponse> getById(
            @RequestHeader(value = UserContext.USER_ID_HEADER, defaultValue = UserContext.DEFAULT_USER_ID) String userId,
            @PathVariable String id
    ) {
        return ResponseEntity.ok(applicationRecordService.getById(userId, id));
    }
}

