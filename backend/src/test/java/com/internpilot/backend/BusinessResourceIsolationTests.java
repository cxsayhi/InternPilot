package com.internpilot.backend;

import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.internpilot.backend.common.UserContext;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class BusinessResourceIsolationTests {

    private static final String USER_A = "phase3-user-a";
    private static final String USER_B = "phase3-user-b";

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void resumeDetailIsScopedByUserId() throws Exception {
        String resumeId = createResume(USER_A);

        mockMvc.perform(get("/api/resumes/{id}", resumeId)
                        .header(UserContext.USER_ID_HEADER, USER_A))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(resumeId));

        mockMvc.perform(get("/api/resumes/{id}", resumeId)
                        .header(UserContext.USER_ID_HEADER, USER_B))
                .andExpect(status().isNotFound());
    }

    @Test
    void projectListOnlyReturnsCurrentUsersProjects() throws Exception {
        createProject(USER_A);

        mockMvc.perform(get("/api/projects")
                        .header(UserContext.USER_ID_HEADER, USER_A))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)));

        mockMvc.perform(get("/api/projects")
                        .header(UserContext.USER_ID_HEADER, USER_B))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }

    @Test
    void applicationListAndDetailAreScopedByUserId() throws Exception {
        String applicationId = createApplication(USER_A);

        mockMvc.perform(get("/api/applications")
                        .header(UserContext.USER_ID_HEADER, USER_A))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)));

        mockMvc.perform(get("/api/applications")
                        .header(UserContext.USER_ID_HEADER, USER_B))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));

        mockMvc.perform(get("/api/applications/{id}", applicationId)
                        .header(UserContext.USER_ID_HEADER, USER_B))
                .andExpect(status().isNotFound());
    }

    private String createResume(String userId) throws Exception {
        String response = mockMvc.perform(post("/api/resumes")
                        .header(UserContext.USER_ID_HEADER, userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "title", "Backend Resume",
                                "rawText", "Java Spring Boot MySQL Redis project experience.",
                                "sourceType", "PASTED_TEXT"
                        ))))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        return objectMapper.readTree(response).get("id").asText();
    }

    private void createProject(String userId) throws Exception {
        mockMvc.perform(post("/api/projects")
                        .header(UserContext.USER_ID_HEADER, userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "name", "Online Shop",
                                "description", "Built backend APIs.",
                                "techStack", List.of("Java", "Spring Boot", "MySQL"),
                                "evidenceText", "Implemented REST APIs and database persistence."
                        ))))
                .andExpect(status().isOk());
    }

    private String createApplication(String userId) throws Exception {
        String response = mockMvc.perform(post("/api/applications")
                        .header(UserContext.USER_ID_HEADER, userId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of(
                                "company", "DemoCo",
                                "role", "Java Backend Intern",
                                "jobText", "Requirements: Java, Spring Boot, MySQL, Redis."
                        ))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("DRAFT"))
                .andReturn()
                .getResponse()
                .getContentAsString();

        return objectMapper.readTree(response).get("id").asText();
    }
}

