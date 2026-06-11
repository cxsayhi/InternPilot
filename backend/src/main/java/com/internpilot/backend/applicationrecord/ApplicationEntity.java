package com.internpilot.backend.applicationrecord;

import com.internpilot.backend.common.TimestampedEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

@Entity
@Table(name = "applications")
public class ApplicationEntity extends TimestampedEntity {

    @Id
    @Column(name = "id", nullable = false, length = 64)
    private String id;

    @Column(name = "user_id", nullable = false, length = 64)
    private String userId;

    @Column(name = "resume_id", length = 64)
    private String resumeId;

    @Column(name = "company", length = 160)
    private String company;

    @Column(name = "role", length = 160)
    private String role;

    @Lob
    @Column(name = "job_text", nullable = false)
    private String jobText;

    @Column(name = "status", nullable = false, length = 32)
    private String status;

    protected ApplicationEntity() {
    }

    public ApplicationEntity(
            String id,
            String userId,
            String resumeId,
            String company,
            String role,
            String jobText,
            String status
    ) {
        this.id = id;
        this.userId = userId;
        this.resumeId = resumeId;
        this.company = company;
        this.role = role;
        this.jobText = jobText;
        this.status = status;
    }

    public String getId() {
        return id;
    }

    public String getResumeId() {
        return resumeId;
    }

    public String getCompany() {
        return company;
    }

    public String getRole() {
        return role;
    }

    public String getJobText() {
        return jobText;
    }

    public String getStatus() {
        return status;
    }
}

