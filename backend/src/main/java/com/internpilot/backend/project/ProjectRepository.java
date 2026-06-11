package com.internpilot.backend.project;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProjectRepository extends JpaRepository<ProjectEntity, String> {

    List<ProjectEntity> findAllByUserIdOrderByCreatedAtDesc(String userId);
}

