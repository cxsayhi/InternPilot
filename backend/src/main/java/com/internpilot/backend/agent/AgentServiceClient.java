package com.internpilot.backend.agent;

import com.internpilot.backend.config.AgentServiceProperties;
import com.internpilot.backend.dto.agent.AgentApplicationAnalysisRequest;
import com.internpilot.backend.dto.agent.AgentApplicationAnalysisResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class AgentServiceClient {

    private final RestClient restClient;

    public AgentServiceClient(RestClient.Builder builder, AgentServiceProperties properties) {
        this.restClient = builder.baseUrl(properties.baseUrl()).build();
    }

    public AgentApplicationAnalysisResponse analyzeApplication(AgentApplicationAnalysisRequest request) {
        return restClient.post()
                .uri("/internal/agent/application-analysis")
                .body(request)
                .retrieve()
                .body(AgentApplicationAnalysisResponse.class);
    }
}
