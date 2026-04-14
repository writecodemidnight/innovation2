package com.campusclub.activity.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "activity_participants")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ActivityParticipant extends BaseEntity {

    @Column(name = "activity_id", nullable = false)
    private Long activityId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    private ParticipationStatus status = ParticipationStatus.REGISTERED;

    @Column(name = "registered_at", nullable = false)
    private LocalDateTime registeredAt = LocalDateTime.now();

    @Column(name = "checked_in_at")
    private LocalDateTime checkedInAt;

    /**
     * Check in participant: REGISTERED -> CHECKED_IN
     */
    public void checkIn() {
        if (this.status != ParticipationStatus.REGISTERED) {
            throw new IllegalStateException("Only REGISTERED participants can check in. Current status: " + this.status);
        }
        this.status = ParticipationStatus.CHECKED_IN;
        this.checkedInAt = LocalDateTime.now();
    }

    /**
     * Cancel participation: REGISTERED -> CANCELLED
     */
    public void cancel() {
        if (this.status != ParticipationStatus.REGISTERED) {
            throw new IllegalStateException("Only REGISTERED participants can cancel. Current status: " + this.status);
        }
        this.status = ParticipationStatus.CANCELLED;
    }

    public enum ParticipationStatus {
        REGISTERED, CHECKED_IN, CANCELLED, NO_SHOW
    }
}
