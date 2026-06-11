package com.internpilot.backend.resume;

import com.internpilot.backend.common.TimestampedEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

@Entity
@Table(name = "resumes")
public class ResumeEntity extends TimestampedEntity {

    @Id
    @Column(name = "id", nullable = false, length = 64)
    private String id;

    @Column(name = "user_id", nullable = false, length = 64)
    private String userId;

    @Column(name = "title", nullable = false, length = 160)
    private String title;

    @Lob
    @Column(name = "raw_text", nullable = false)
    private String rawText;

    @Column(name = "source_type", nullable = false, length = 32)
    private String sourceType;

    @Column(name = "is_active", nullable = false)
    private boolean active;

    protected ResumeEntity() {
    }

    public ResumeEntity(String id, String userId, String title, String rawText, String sourceType) {
        this.id = id;
        this.userId = userId;
        this.title = title;
        this.rawText = rawText;
        this.sourceType = sourceType;
        this.active = true;
    }

    public String getId() {
        return id;
    }

    public String getUserId() {
        return userId;
    }

    public String getTitle() {
        return title;
    }

    public String getRawText() {
        return rawText;
    }

    public String getSourceType() {
        return sourceType;
    }

    public boolean isActive() {
        return active;
    }
}

