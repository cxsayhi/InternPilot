package com.internpilot.backend.resume;

import com.internpilot.backend.common.IdGenerator;
import com.internpilot.backend.user.UserService;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class ResumeService {

    private final ResumeRepository resumeRepository;
    private final UserService userService;

    public ResumeService(ResumeRepository resumeRepository, UserService userService) {
        this.resumeRepository = resumeRepository;
        this.userService = userService;
    }

    @Transactional
    public ResumeResponse create(String userId, ResumeCreateRequest request) {
        userService.ensureUserExists(userId);
        String sourceType = request.sourceType() == null || request.sourceType().isBlank()
                ? "PASTED_TEXT"
                : request.sourceType();
        ResumeEntity entity = new ResumeEntity(
                IdGenerator.prefixedId("resume"),
                userId,
                request.title(),
                request.rawText(),
                sourceType
        );
        return ResumeResponse.fromEntity(resumeRepository.save(entity));
    }

    @Transactional(readOnly = true)
    public ResumeResponse getById(String userId, String id) {
        return resumeRepository.findByIdAndUserId(id, userId)
                .map(ResumeResponse::fromEntity)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Resume not found."));
    }
}

