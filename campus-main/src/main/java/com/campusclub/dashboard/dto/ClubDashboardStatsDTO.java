package com.campusclub.dashboard.dto;

import lombok.Data;

import java.math.BigDecimal;

/**
 * 社团仪表盘统计数据 DTO
 */
@Data
public class ClubDashboardStatsDTO {

    /** 本月活动数 */
    private Integer monthlyActivities;

    /** 本月活动增长率 */
    private Double monthlyGrowthRate;

    /** 参与人次 */
    private Integer totalParticipants;

    /** 平均评分 */
    private BigDecimal averageRating;

    /** 资源利用率 */
    private Double resourceUtilizationRate;

    /** 待审批申请数 */
    private Integer pendingApprovals;

    /** 进行中活动数 */
    private Integer ongoingActivities;

    /** 已结束活动数 */
    private Integer completedActivities;
}
