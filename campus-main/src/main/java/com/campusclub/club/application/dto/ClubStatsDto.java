package com.campusclub.club.application.dto;

import lombok.Builder;
import lombok.Data;

/**
 * 社团统计数据DTO
 */
@Data
@Builder
public class ClubStatsDto {
    /** 活动总数 */
    private Integer activityCount;

    /** 总参与人数 */
    private Integer totalParticipants;

    /** 待审批活动数 */
    private Integer pendingCount;

    /** 进行中活动数 */
    private Integer ongoingCount;

    /** 已完成活动数 */
    private Integer completedCount;

    /** 本月活动数 */
    private Integer thisMonthActivityCount;

    /** 平均评分 */
    private Double averageRating;
}
