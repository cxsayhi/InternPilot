package com.internpilot.backend.project;

import com.internpilot.backend.common.TimestampedEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

@Entity
@Table(name = "projects")
public class ProjectEntity extends TimestampedEntity {

    @Id
    @Column(name = "id", nullable = false, length = 64)
    private String id;

    @Column(name = "user_id", nullable = false, length = 64)
    private String userId;

    @Column(name = "resume_id", length = 64)
    private String resumeId;

    @Column(name = "name", nullable = false, length = 160)
    private String name;

    @Lob
    @Column(name = "description")
    private String description;

    @Column(name = "tech_stack")
    private String techStackJson;

    @Lob
    @Column(name = "evidence_text")
    private String evidenceText;

    protected ProjectEntity() {
    }

    public ProjectEntity(
            String id,
            String userId,
            String resumeId,
            String name,
            String description,
            String techStackJson,
            String evidenceText
    ) {
        this.id = id;
        this.userId = userId;
        this.resumeId = resumeId;
        this.name = name;
        this.description = description;
        this.techStackJson = techStackJson;
        this.evidenceText = evidenceText;
    }

    public String getId() {
        return id;
    }

    public String getResumeId() {
        return resumeId;
    }

    public String getName() {
        return name;
    }

    public String getDescription() {
        return description;
    }

    public String getTechStackJson() {
        return techStackJson;
    }

    public String getEvidenceText() {
        return evidenceText;
    }
}

