package com.campusclub.dashboard.service.impl;

import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.dashboard.dto.ClubDashboardStatsDTO;
import com.campusclub.dashboard.service.DashboardService;
import com.campusclub.resource.domain.repository.ResourceBookingRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.temporal.TemporalAdjusters;

/**
 * 仪表盘服务实现
 */
@Service
@RequiredArgsConstructor
public class DashboardServiceImpl implements DashboardService {

    private final ActivityRepository activityRepository;
    private final ResourceBookingRepository bookingRepository;

    @Override
    public ClubDashboardStatsDTO getClubStats(Long clubId) {
        ClubDashboardStatsDTO stats = new ClubDashboardStatsDTO();

        // 本月活动数
        LocalDateTime monthStart = LocalDateTime.now().with(TemporalAdjusters.firstDayOfMonth()).withHour(0).withMinute(0);
        LocalDateTime monthEnd = LocalDateTime.now().with(TemporalAdjusters.lastDayOfMonth()).withHour(23).withMinute(59);
        Integer monthlyActivities = activityRepository.countByClubIdAndStartTimeBetween(clubId, monthStart, monthEnd);
        stats.setMonthlyActivities(monthlyActivities != null ? monthlyActivities : 0);

        // 上月活动数（用于计算增长率）
        LocalDateTime lastMonthStart = monthStart.minusMonths(1);
        LocalDateTime lastMonthEnd = monthStart.minusSeconds(1);
        Integer lastMonthActivities = activityRepository.countByClubIdAndStartTimeBetween(clubId, lastMonthStart, lastMonthEnd);

        // 计算增长率
        if (lastMonthActivities != null && lastMonthActivities > 0) {
            double growthRate = ((double) stats.getMonthlyActivities() - lastMonthActivities) / lastMonthActivities * 100;
            stats.setMonthlyGrowthRate(Math.round(growthRate * 10.0) / 10.0);
        } else {
            stats.setMonthlyGrowthRate(0.0);
        }

        // 参与人次
        Integer totalParticipants = activityRepository.sumParticipantsByClubId(clubId);
        stats.setTotalParticipants(totalParticipants != null ? totalParticipants : 0);

        // 平均评分
        Double avgRating = activityRepository.getAverageRatingByClubId(clubId);
        stats.setAverageRating(avgRating != null ?
            BigDecimal.valueOf(avgRating).setScale(1, RoundingMode.HALF_UP) :
            BigDecimal.ZERO);

        // 资源利用率（简化计算：基于预约数量）
        // 通过activity关联查询社团的预约数量
        Long bookingCount = bookingRepository.countApprovedBookingsByClubAndTimeRange(clubId, monthStart, monthEnd);
        // 假设每个社团每月有10个资源，每个资源可预约30次，总共300次预约机会
        Double utilizationRate = bookingCount != null && bookingCount > 0 ?
            Math.min(100.0, bookingCount * 0.33) : 0.0; // 简化计算
        stats.setResourceUtilizationRate(Math.round(utilizationRate * 10.0) / 10.0);

        // 待审批申请数
        Integer pendingApprovals = activityRepository.countPendingByClubId(clubId);
        stats.setPendingApprovals(pendingApprovals != null ? pendingApprovals : 0);

        // 进行中活动数
        Integer ongoingActivities = activityRepository.countOngoingByClubId(clubId, LocalDateTime.now());
        stats.setOngoingActivities(ongoingActivities != null ? ongoingActivities : 0);

        // 已结束活动数
        Integer completedActivities = activityRepository.countCompletedByClubId(clubId);
        stats.setCompletedActivities(completedActivities != null ? completedActivities : 0);

        return stats;
    }
}
