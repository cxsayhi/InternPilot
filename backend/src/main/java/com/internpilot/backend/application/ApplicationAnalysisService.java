package com.internpilot.backend.application;

import com.internpilot.backend.agent.AgentServiceClient;
import com.internpilot.backend.domain.ApplicationAnalysisRecord;
import com.internpilot.backend.dto.AnalyzeApplicationRequest;
import com.internpilot.backend.dto.AnalyzeApplicationResponse;
import com.internpilot.backend.dto.MatchResultDTO;
import com.internpilot.backend.dto.RewriteSuggestionDTO;
import com.internpilot.backend.dto.agent.AgentApplicationAnalysisRequest;
import com.internpilot.backend.dto.agent.AgentApplicationAnalysisResponse;
import com.internpilot.backend.dto.agent.AgentRewriteSuggestionDTO;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.server.ResponseStatusException;

@Service
public class ApplicationAnalysisService {

    private static final String STATUS_ANALYZED = "ANALYZED";
    private static final String STATUS_FAILED = "FAILED";
    private static final String SUGGESTION_PENDING_REVIEW = "PENDING_REVIEW";

    private final AgentServiceClient agentServiceClient;
    private final InMemoryApplicationAnalysisStore store;

    public ApplicationAnalysisService(
            AgentServiceClient agentServiceClient,
            InMemoryApplicationAnalysisStore store
    ) {
        this.agentServiceClient = agentServiceClient;
        this.store = store;
    }

    public AnalyzeApplicationResponse analyze(String userId, AnalyzeApplicationRequest request) {
        String applicationId = prefixedId("app");
        String analysisId = prefixedId("analysis");

        AgentApplicationAnalysisRequest agentRequest = new AgentApplicationAnalysisRequest(
                userId,
                applicationId,
                request.resumeText(),
                request.jobText(),
                request.company(),
                request.role()
        );

        AgentApplicationAnalysisResponse agentResponse;
        try {
            agentResponse = agentServiceClient.analyzeApplication(agentRequest);
        } catch (RestClientException ex) {
            store.save(new ApplicationAnalysisRecord(
                    applicationId,
                    analysisId,
                    userId,
                    STATUS_FAILED,
                    null,
                    "AGENT_ANALYSIS_FAILED",
                    Instant.now()
            ));
            throw new ResponseStatusException(
                    HttpStatus.BAD_GATEWAY,
                    "Application analysis failed. Please try again later.",
                    ex
            );
        }

        if (agentResponse == null) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_GATEWAY,
                    "Application analysis failed. Please try again later."
            );
        }

        MatchResultDTO matchResult = new MatchResultDTO(
                agentResponse.matchScore(),
                mapOrEmpty(agentResponse.scoreBreakdown()),
                listOrEmpty(agentResponse.strongMatches()),
                listOrEmpty(agentResponse.weakMatches()),
                listOrEmpty(agentResponse.missingSkills())
        );

        List<RewriteSuggestionDTO> suggestions = listOrEmpty(agentResponse.rewriteSuggestions())
                .stream()
                .map(this::toPendingSuggestion)
                .toList();

        AnalyzeApplicationResponse response = new AnalyzeApplicationResponse(
                applicationId,
                analysisId,
                STATUS_ANALYZED,
                matchResult,
                suggestions,
                listOrEmpty(agentResponse.learningPlan()),
                listOrEmpty(agentResponse.warnings())
        );

        store.save(new ApplicationAnalysisRecord(
                applicationId,
                analysisId,
                userId,
                STATUS_ANALYZED,
                response,
                null,
                Instant.now()
        ));

        return response;
    }

    private RewriteSuggestionDTO toPendingSuggestion(AgentRewriteSuggestionDTO suggestion) {
        String rewrittenBullet = firstNonBlank(
                suggestion.rewrittenBullet(),
                suggestion.suggestedBullet()
        );
        return new RewriteSuggestionDTO(
                prefixedId("sug"),
                SUGGESTION_PENDING_REVIEW,
                suggestion.originalBullet(),
                rewrittenBullet,
                rewrittenBullet,
                listOrEmpty(suggestion.targetedSkills()),
                listOrEmpty(suggestion.evidenceSources()),
                listOrEmpty(suggestion.unsupportedClaims()),
                suggestion.confidence(),
                suggestion.needsUserConfirmation()
        );
    }

    private static String prefixedId(String prefix) {
        return prefix + "_" + UUID.randomUUID();
    }

    private static <T> List<T> listOrEmpty(List<T> value) {
        return value == null ? List.of() : value;
    }

    private static Map<String, Integer> mapOrEmpty(Map<String, Integer> value) {
        return value == null ? Map.of() : value;
    }

    private static String firstNonBlank(String primary, String fallback) {
        if (primary != null && !primary.isBlank()) {
            return primary;
        }
        return fallback;
    }
}
