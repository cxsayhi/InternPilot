package com.internpilot.backend.project;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.internpilot.backend.common.IdGenerator;
import com.internpilot.backend.resume.ResumeRepository;
import com.internpilot.backend.user.UserService;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class ProjectService {

    private static final TypeReference<List<String>> STRING_LIST = new TypeReference<>() {
    };

    private final ProjectRepository projectRepository;
    private final ResumeRepository resumeRepository;
    private final UserService userService;
    private final ObjectMapper objectMapper;

    public ProjectService(
            ProjectRepository projectRepository,
            ResumeRepository resumeRepository,
            UserService userService,
            ObjectMapper objectMapper
    ) {
        this.projectRepository = projectRepository;
        this.resumeRepository = resumeRepository;
        this.userService = userService;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public ProjectResponse create(String userId, ProjectCreateRequest request) {
        userService.ensureUserExists(userId);
        assertResumeOwnedByUser(userId, request.resumeId());

        ProjectEntity entity = new ProjectEntity(
                IdGenerator.prefixedId("project"),
                userId,
                blankToNull(request.resumeId()),
                request.name(),
                request.description(),
                toJson(listOrEmpty(request.techStack())),
                request.evidenceText()
        );

        return toResponse(projectRepository.save(entity));
    }

    @Transactional(readOnly = true)
    public List<ProjectResponse> list(String userId) {
        return projectRepository.findAllByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(this::toResponse)
                .toList();
    }

    private void assertResumeOwnedByUser(String userId, String resumeId) {
        if (resumeId == null || resumeId.isBlank()) {
            return;
        }
        if (!resumeRepository.existsByIdAndUserId(resumeId, userId)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Resume not found.");
        }
    }

    private ProjectResponse toResponse(ProjectEntity entity) {
        return new ProjectResponse(
                entity.getId(),
                entity.getResumeId(),
                entity.getName(),
                entity.getDescription(),
                fromJson(entity.getTechStackJson()),
                entity.getEvidenceText(),
                entity.getCreatedAt(),
                entity.getUpdatedAt()
        );
    }

    private String toJson(List<String> values) {
        try {
            return objectMapper.writeValueAsString(values);
        } catch (JsonProcessingException ex) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Invalid tech stack.", ex);
        }
    }

    private List<String> fromJson(String json) {
        if (json == null || json.isBlank()) {
            return List.of();
        }
        try {
            return objectMapper.readValue(json, STRING_LIST);
        } catch (JsonProcessingException ex) {
            return List.of();
        }
    }

    private static List<String> listOrEmpty(List<String> values) {
        return values == null ? List.of() : values;
    }

    private static String blankToNull(String value) {
        return value == null || value.isBlank() ? null : value;
    }
}

