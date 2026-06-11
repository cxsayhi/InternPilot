package com.internpilot.backend.resume;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ResumeRepository extends JpaRepository<ResumeEntity, String> {

    Optional<ResumeEntity> findByIdAndUserId(String id, String userId);

    boolean existsByIdAndUserId(String id, String userId);
}
