package com.internpilot.backend.application;

import com.internpilot.backend.domain.ApplicationAnalysisRecord;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import org.springframework.stereotype.Component;

@Component
public class InMemoryApplicationAnalysisStore {

    private final ConcurrentMap<String, ApplicationAnalysisRecord> records = new ConcurrentHashMap<>();

    public void save(ApplicationAnalysisRecord record) {
        records.put(record.applicationId(), record);
    }

    public Optional<ApplicationAnalysisRecord> findByApplicationId(String applicationId) {
        return Optional.ofNullable(records.get(applicationId));
    }
}

