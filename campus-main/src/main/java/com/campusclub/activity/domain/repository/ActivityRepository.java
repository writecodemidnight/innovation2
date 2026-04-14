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

    Page<Activity> findByClubId(Long clubId, Pageable pageable);

    Page<Activity> findByClubIdAndStatus(Long clubId, Activity.ActivityStatus status, Pageable pageable);

    List<Activity> findByCreatedBy(Long createdBy);

    Page<Activity> findByActivityType(Activity.ActivityType type, Pageable pageable);

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
}
