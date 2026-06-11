package com.internpilot.backend.applicationrecord;

import com.internpilot.backend.common.IdGenerator;
import com.internpilot.backend.resume.ResumeRepository;
import com.internpilot.backend.user.UserService;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class ApplicationRecordService {

    private static final String STATUS_DRAFT = "DRAFT";

    private final ApplicationRepository applicationRepository;
    private final ResumeRepository resumeRepository;
    private final UserService userService;

    public ApplicationRecordService(
            ApplicationRepository applicationRepository,
            ResumeRepository resumeRepository,
            UserService userService
    ) {
        this.applicationRepository = applicationRepository;
        this.resumeRepository = resumeRepository;
        this.userService = userService;
    }

    @Transactional
    public ApplicationResponse create(String userId, ApplicationCreateRequest request) {
        userService.ensureUserExists(userId);
        assertResumeOwnedByUser(userId, request.resumeId());

        ApplicationEntity entity = new ApplicationEntity(
                IdGenerator.prefixedId("app"),
                userId,
                blankToNull(request.resumeId()),
                request.company(),
                request.role(),
                request.jobText(),
                STATUS_DRAFT
        );

        return ApplicationResponse.fromEntity(applicationRepository.save(entity));
    }

    @Transactional(readOnly = true)
    public List<ApplicationResponse> list(String userId) {
        return applicationRepository.findAllByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(ApplicationResponse::fromEntity)
                .toList();
    }

    @Transactional(readOnly = true)
    public ApplicationResponse getById(String userId, String id) {
        return applicationRepository.findByIdAndUserId(id, userId)
                .map(ApplicationResponse::fromEntity)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Application not found."));
    }

    private void assertResumeOwnedByUser(String userId, String resumeId) {
        if (resumeId == null || resumeId.isBlank()) {
            return;
        }
        if (!resumeRepository.existsByIdAndUserId(resumeId, userId)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Resume not found.");
        }
    }

    private static String blankToNull(String value) {
        return value == null || value.isBlank() ? null : value;
    }
}

