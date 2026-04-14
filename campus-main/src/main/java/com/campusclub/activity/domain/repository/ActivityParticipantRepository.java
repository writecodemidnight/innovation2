package com.campusclub.activity.domain.repository;

import com.campusclub.activity.domain.entity.ActivityParticipant;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ActivityParticipantRepository extends JpaRepository<ActivityParticipant, Long> {

    List<ActivityParticipant> findByActivityId(Long activityId);

    List<ActivityParticipant> findByUserId(Long userId);

    Optional<ActivityParticipant> findByActivityIdAndUserId(Long activityId, Long userId);

    boolean existsByActivityIdAndUserId(Long activityId, Long userId);

    long countByActivityId(Long activityId);

    long countByActivityIdAndStatus(Long activityId, ActivityParticipant.ParticipationStatus status);

    @Query("SELECT ap FROM ActivityParticipant ap WHERE ap.userId = :userId AND ap.status = 'REGISTERED'")
    List<ActivityParticipant> findActiveRegistrationsByUserId(@Param("userId") Long userId);
}
