package com.campusclub.resource.domain.repository;

import com.campusclub.resource.domain.entity.ResourceBooking;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ResourceBookingRepository extends JpaRepository<ResourceBooking, Long> {

    /**
     * 查询用户的预约列表
     */
    List<ResourceBooking> findByApplicantIdAndDeletedFalseOrderByCreatedAtDesc(Long applicantId);

    /**
     * 查询活动的预约
     */
    List<ResourceBooking> findByActivityIdAndDeletedFalse(Long activityId);

    /**
     * 查询资源的预约列表
     */
    List<ResourceBooking> findByResourceIdAndDeletedFalse(Long resourceId);

    /**
     * 查询资源在时间段内的冲突预约
     */
    @Query("SELECT b FROM ResourceBooking b WHERE b.resourceId = :resourceId " +
           "AND b.deleted = false AND b.status NOT IN ('REJECTED', 'CANCELLED') " +
           "AND ((b.startTime <= :endTime AND b.endTime >= :startTime))")
    List<ResourceBooking> findConflictingBookings(
            @Param("resourceId") Long resourceId,
            @Param("startTime") LocalDateTime startTime,
            @Param("endTime") LocalDateTime endTime
    );

    /**
     * 查询用户的预约数量
     */
    long countByApplicantIdAndStatusAndDeletedFalse(Long applicantId, String status);

    /**
     * 计算用户在时间段内的资源预约数
     */
    @Query("SELECT COUNT(b) FROM ResourceBooking b " +
           "WHERE b.applicantId = :applicantId AND b.deleted = false " +
           "AND b.status IN ('APPROVED', 'COMPLETED') " +
           "AND b.startTime >= :start AND b.endTime <= :end")
    Long countApprovedBookingsByApplicantAndTimeRange(@Param("applicantId") Long applicantId,
                                                       @Param("start") LocalDateTime start,
                                                       @Param("end") LocalDateTime end);

    /**
     * 计算社团在时间段内的资源预约数（通过activity关联）
     */
    @Query("SELECT COUNT(b) FROM ResourceBooking b JOIN Activity a ON b.activityId = a.id " +
           "WHERE a.clubId = :clubId AND b.deleted = false " +
           "AND b.status IN ('APPROVED', 'COMPLETED') " +
           "AND b.startTime >= :start AND b.endTime <= :end")
    Long countApprovedBookingsByClubAndTimeRange(@Param("clubId") Long clubId,
                                                  @Param("start") LocalDateTime start,
                                                  @Param("end") LocalDateTime end);

    /**
     * 根据状态统计预约数量
     */
    long countByStatus(String status);

    /**
     * 统计时间段内的预约数量
     */
    long countByStartTimeBetween(LocalDateTime start, LocalDateTime end);

    /**
     * 根据状态和删除标志查询预约列表
     */
    List<ResourceBooking> findByStatusAndDeletedFalse(String status);
}
