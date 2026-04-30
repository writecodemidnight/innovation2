package com.campusclub.feedback.domain.repository;

import com.campusclub.feedback.domain.entity.Feedback;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 反馈评价仓库接口
 */
@Repository
public interface FeedbackRepository extends JpaRepository<Feedback, Long> {

    /**
     * 根据活动ID查询反馈列表
     */
    Page<Feedback> findByActivityId(Long activityId, Pageable pageable);

    /**
     * 根据用户ID查询反馈列表
     */
    Page<Feedback> findByUserId(Long userId, Pageable pageable);

    /**
     * 根据活动ID和用户ID查询反馈
     */
    Optional<Feedback> findByActivityIdAndUserId(Long activityId, Long userId);

    /**
     * 检查用户是否已对活动进行评价
     */
    boolean existsByActivityIdAndUserId(Long activityId, Long userId);

    /**
     * 获取活动的评分分布统计
     */
    @Query("SELECT f.rating, COUNT(f) FROM Feedback f WHERE f.activityId = :activityId GROUP BY f.rating")
    List<Object[]> getRatingDistribution(@Param("activityId") Long activityId);

    /**
     * 获取活动的平均评分
     */
    @Query("SELECT AVG(f.rating) FROM Feedback f WHERE f.activityId = :activityId")
    Double getAverageRating(@Param("activityId") Long activityId);

    /**
     * 获取活动的平均组织评分
     */
    @Query("SELECT AVG(f.organizationRating) FROM Feedback f WHERE f.activityId = :activityId AND f.organizationRating IS NOT NULL")
    Double getAverageOrganizationRating(@Param("activityId") Long activityId);

    /**
     * 获取活动的平均内容评分
     */
    @Query("SELECT AVG(f.contentRating) FROM Feedback f WHERE f.activityId = :activityId AND f.contentRating IS NOT NULL")
    Double getAverageContentRating(@Param("activityId") Long activityId);

    /**
     * 获取活动的评价总数
     */
    long countByActivityId(Long activityId);

    /**
     * 根据评分筛选
     */
    Page<Feedback> findByActivityIdAndRating(Long activityId, Integer rating, Pageable pageable);
}
