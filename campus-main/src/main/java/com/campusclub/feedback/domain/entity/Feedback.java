package com.campusclub.feedback.domain.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 活动反馈评价实体
 */
@Entity
@Table(name = "feedback")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Feedback {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "activity_id", nullable = false)
    private Long activityId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(nullable = false)
    private Integer rating;

    @Column(name = "organization_rating")
    private Integer organizationRating;

    @Column(name = "content_rating")
    private Integer contentRating;

    @Column(length = 2000)
    private String content;

    @ElementCollection
    @CollectionTable(name = "feedback_images", joinColumns = @JoinColumn(name = "feedback_id"))
    @Column(name = "image_url")
    private List<String> images;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // ========== NLP情感分析结果 ==========

    @Column(name = "sentiment_score")
    private Double sentimentScore;

    @Column(name = "sentiment_level", length = 20)
    private String sentimentLevel;

    @Column(name = "sentiment_confidence")
    private Double sentimentConfidence;

    @ElementCollection
    @CollectionTable(name = "feedback_keywords", joinColumns = @JoinColumn(name = "feedback_id"))
    @Column(name = "keyword")
    private List<String> keywords;
}
