package com.internpilot.backend.applicationrecord;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ApplicationRepository extends JpaRepository<ApplicationEntity, String> {

    List<ApplicationEntity> findAllByUserIdOrderByCreatedAtDesc(String userId);

    Optional<ApplicationEntity> findByIdAndUserId(String id, String userId);
}

