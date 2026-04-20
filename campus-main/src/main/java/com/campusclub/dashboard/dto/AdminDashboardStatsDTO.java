package com.campusclub.dashboard.dto;

import lombok.Data;

import java.math.BigDecimal;

/**
 * 管理端仪表盘统计数据DTO
 * 包含系统全局统计数据
 */
@Data
public class AdminDashboardStatsDTO {

    // 基础统计
    private Integer totalClubs;           // 社团总数
    private Integer totalActivities;      // 活动总数
    private Integer totalUsers;           // 用户总数
    private Integer totalParticipants;    // 总参与人次

    // 活动统计
    private Integer ongoingActivities;    // 进行中活动数
    private Integer pendingActivities;    // 待审批活动数
    private Integer completedActivities;  // 已完成活动数
    private Integer todayActivities;      // 今日活动数

    // 审批统计
    private Integer pendingApprovals;     // 待审批总数
    private Integer pendingFundApprovals; // 待审批资金申请

    // 资源统计
    private Integer totalResources;       // 资源总数
    private Integer occupiedResources;    // 已占用资源数
    private BigDecimal resourceUtilizationRate; // 资源利用率

    // 趋势数据
    private Double activityGrowthRate;    // 活动增长率
    private Double participantGrowthRate; // 参与人次增长率
}
