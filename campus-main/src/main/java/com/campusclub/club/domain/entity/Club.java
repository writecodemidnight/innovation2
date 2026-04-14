package com.campusclub.club.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "clubs")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Club extends BaseEntity {

    @Column(name = "name", nullable = false, length = 100)
    private String name;

    @Column(name = "code", unique = true, length = 50)
    private String code;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(name = "category", length = 50)
    private ClubCategory category;

    @Column(name = "logo_url", length = 500)
    private String logoUrl;

    @Column(name = "president_id")
    private Long presidentId;

    @Column(name = "faculty_advisor", length = 100)
    private String facultyAdvisor;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 20)
    private ClubStatus status = ClubStatus.ACTIVE;

    @Column(name = "member_count")
    private Integer memberCount = 0;

    public enum ClubCategory {
        ACADEMIC, ARTS, SPORTS, VOLUNTEER, TECHNOLOGY, CULTURE, OTHER
    }

    public enum ClubStatus {
        ACTIVE, INACTIVE, SUSPENDED
    }
}
