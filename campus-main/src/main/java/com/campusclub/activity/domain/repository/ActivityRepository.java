package com.campusclub.activity.domain.repository;

import com.campusclub.activity.domain.entity.Activity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ActivityRepository extends JpaRepository<Activity, Long> {

    Page<Activity> findByStatus(Activity.ActivityStatus status, Pageable pageable);

    Page<Activity> findByTitleContainingIgnoreCase(String title, Pageable pageable);

    Page<Activity> findByStatusAndTitleContainingIgnoreCase(Activity.ActivityStatus status, String title, Pageable pageable);

    Page<Activity> findByClubId(Long clubId, Pageable pageable);

    Page<Activity> findByClubIdAndStatus(Long clubId, Activity.ActivityStatus status, Pageable pageable);

    // ========== 过滤已删除的活动 ==========

    @Query("SELECT a FROM Activity a WHERE a.deleted = false")
    Page<Activity> findAllActive(Pageable pageable);

    @Query("SELECT a FROM Activity a WHERE a.deleted = false AND a.status = :status")
    Page<Activity> findByStatusAndDeletedFalse(@Param("status") Activity.ActivityStatus status, Pageable pageable);

    @Query("SELECT a FROM Activity a WHERE a.deleted = false AND LOWER(a.title) LIKE LOWER(CONCAT('%', :title, '%'))")
    Page<Activity> findByTitleContainingIgnoreCaseAndDeletedFalse(@Param("title") String title, Pageable pageable);

    @Query("SELECT a FROM Activity a WHERE a.deleted = false AND a.status = :status AND LOWER(a.title) LIKE LOWER(CONCAT('%', :title, '%'))")
    Page<Activity> findByStatusAndTitleContainingIgnoreCaseAndDeletedFalse(
            @Param("status") Activity.ActivityStatus status,
            @Param("title") String title,
            Pageable pageable);

    List<Activity> findByCreatedBy(Long createdBy);

    Page<Activity> findByActivityType(Activity.ActivityType type, Pageable pageable);

    /**
     * 获取已批准/可报名的公开活动列表
     */
    @Query("SELECT a FROM Activity a WHERE a.status IN ('APPROVED', 'REGISTERING')")
    Page<Activity> findPublicActivities(Pageable pageable);

    /**
     * 根据类型获取已批准的公开活动
     */
    @Query("SELECT a FROM Activity a WHERE a.status IN ('APPROVED', 'REGISTERING') AND a.activityType = :type")
    Page<Activity> findPublicActivitiesByType(@Param("type") Activity.ActivityType type, Pageable pageable);

    @Query("SELECT a FROM Activity a WHERE a.status = :status AND a.startTime <= :time")
    List<Activity> findByStatusAndStartTimeBefore(
            @Param("status") Activity.ActivityStatus status,
            @Param("time") LocalDateTime time);

    @Query("SELECT a FROM Activity a WHERE a.status = :status AND a.endTime <= :time")
    List<Activity> findByStatusAndEndTimeBefore(
            @Param("status") Activity.ActivityStatus status,
            @Param("time") LocalDateTime time);

    @Query("SELECT a FROM Activity a WHERE a.status IN ('APPROVED', 'REGISTERING', 'ONGOING') " +
           "AND a.startTime BETWEEN :start AND :end")
    List<Activity> findActiveActivitiesInTimeRange(
            @Param("start") LocalDateTime start,
            @Param("end") LocalDateTime end);

    /**
     * Atomically increment participant count with capacity check.
     * Returns the number of rows updated (1 if successful, 0 if capacity reached).
     */
    @Query("UPDATE Activity a SET a.currentParticipants = a.currentParticipants + 1 " +
           "WHERE a.id = :id AND a.status = 'REGISTERING' " +
           "AND (a.capacity IS NULL OR a.currentParticipants < a.capacity)")
    @Modifying
    int incrementParticipants(@Param("id") Long id);

    /**
     * Atomically decrement participant count, ensuring it doesn't go below 0.
     */
    @Query("UPDATE Activity a SET a.currentParticipants = a.currentParticipants - 1 " +
           "WHERE a.id = :id AND a.currentParticipants > 0")
    @Modifying
    int decrementParticipants(@Param("id") Long id);

    // ========== Dashboard Statistics Methods ==========

    @Query("SELECT COUNT(a) FROM Activity a WHERE a.clubId = :clubId AND a.startTime BETWEEN :start AND :end")
    Integer countByClubIdAndStartTimeBetween(@Param("clubId") Long clubId,
                                               @Param("start") LocalDateTime start,
                                               @Param("end") LocalDateTime end);

    @Query("SELECT COALESCE(SUM(a.currentParticipants), 0) FROM Activity a WHERE a.clubId = :clubId")
    Integer sumParticipantsByClubId(@Param("clubId") Long clubId);

    /**
     * 统计社团已结束活动的参与人次总和
     */
    @Query("SELECT COALESCE(SUM(a.currentParticipants), 0) FROM Activity a WHERE a.clubId = :clubId AND a.status = :status")
    Integer sumParticipantsByClubIdAndStatus(@Param("clubId") Long clubId, @Param("status") Activity.ActivityStatus status);

    // Note: Activity entity doesn't have averageRating field
    // This is a placeholder - actual rating should come from evaluation/feedback table
    @Query("SELECT AVG(4.5) FROM Activity a WHERE a.clubId = :clubId")
    Double getAverageRatingByClubId(@Param("clubId") Long clubId);

    @Query("SELECT COUNT(a) FROM Activity a WHERE a.clubId = :clubId AND a.status = 'PENDING_APPROVAL'")
    Integer countPendingByClubId(@Param("clubId") Long clubId);

    @Query("SELECT COUNT(a) FROM Activity a WHERE a.clubId = :clubId AND a.status = 'ONGOING' " +
           "AND a.startTime <= :now AND a.endTime >= :now")
    Integer countOngoingByClubId(@Param("clubId") Long clubId, @Param("now") LocalDateTime now);

    @Query("SELECT COUNT(a) FROM Activity a WHERE a.clubId = :clubId AND a.status = 'COMPLETED'")
    Integer countCompletedByClubId(@Param("clubId") Long clubId);

    // ========== Admin Dashboard Methods ==========

    @Query("SELECT COALESCE(SUM(a.currentParticipants), 0) FROM Activity a")
    Integer sumAllParticipants();

    int countByStatus(Activity.ActivityStatus status);

    int countByStartTimeBetween(LocalDateTime start, LocalDateTime end);

    int countByClubId(Long clubId);

    // ========== Recommendation Methods ==========

    /**
     * 获取热门活动（按当前参与人数排序）
     */
    @Query("SELECT a FROM Activity a WHERE a.status IN ('APPROVED', 'REGISTERING', 'ONGOING') " +
           "ORDER BY a.currentParticipants DESC")
    List<Activity> findHotActivities(Pageable pageable);

    /**
     * 获取即将开始的活动
     */
    @Query("SELECT a FROM Activity a WHERE a.status IN ('APPROVED', 'REGISTERING') " +
           "AND a.startTime > :now AND a.startTime <= :endTime " +
           "ORDER BY a.startTime ASC")
    List<Activity> findUpcomingActivities(@Param("now") LocalDateTime now,
                                          @Param("endTime") LocalDateTime endTime,
                                          Pageable pageable);

    /**
     * 获取推荐活动（基于用户兴趣的简化版：按类型匹配和参与人数排序）
     * 实际生产环境应该使用协同过滤或基于内容的推荐算法
     */
    @Query("SELECT a FROM Activity a WHERE a.status IN ('APPROVED', 'REGISTERING') " +
           "AND (:preferredType IS NULL OR a.activityType = :preferredType) " +
           "ORDER BY a.currentParticipants DESC, a.startTime ASC")
    List<Activity> findRecommendedActivities(@Param("preferredType") Activity.ActivityType preferredType,
                                             Pageable pageable);

    // ========== Activity Trend Methods ==========

    /**
     * 按日期统计社团活动数量（用于趋势图）
     */
    @Query("SELECT DATE(a.startTime) as date, COUNT(a) as count " +
           "FROM Activity a WHERE a.clubId = :clubId " +
           "AND a.startTime BETWEEN :start AND :end " +
           "GROUP BY DATE(a.startTime) ORDER BY DATE(a.startTime)")
    List<Object[]> countActivitiesByDate(@Param("clubId") Long clubId,
                                         @Param("start") LocalDateTime start,
                                         @Param("end") LocalDateTime end);

    /**
     * 统计社团各类型活动数量（用于饼图）
     */
    @Query("SELECT a.activityType as type, COUNT(a) as count " +
           "FROM Activity a WHERE a.clubId = :clubId " +
           "GROUP BY a.activityType")
    List<Object[]> countActivitiesByType(@Param("clubId") Long clubId);
}
