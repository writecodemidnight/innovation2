package com.campusclub.dashboard.service.impl;

import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.club.domain.repository.ClubRepository;
import com.campusclub.dashboard.dto.AdminDashboardStatsDTO;
import com.campusclub.dashboard.service.AdminDashboardService;
import com.campusclub.fund.domain.entity.FundApplication;
import com.campusclub.fund.repository.FundApplicationRepository;
import com.campusclub.resource.domain.entity.ResourceBooking;
import com.campusclub.resource.domain.repository.ResourceBookingRepository;
import com.campusclub.user.domain.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.TemporalAdjusters;
import java.util.*;

/**
 * 管理端仪表盘服务实现
 */
@Service
@RequiredArgsConstructor
public class AdminDashboardServiceImpl implements AdminDashboardService {

    private final ClubRepository clubRepository;
    private final ActivityRepository activityRepository;
    private final UserRepository userRepository;
    private final ResourceBookingRepository bookingRepository;
    private final FundApplicationRepository fundApplicationRepository;

    @Override
    public AdminDashboardStatsDTO getGlobalStats() {
        AdminDashboardStatsDTO stats = new AdminDashboardStatsDTO();

        // 基础统计
        stats.setTotalClubs((int) clubRepository.count());
        stats.setTotalActivities((int) activityRepository.count());
        stats.setTotalUsers((int) userRepository.count());

        // 计算总参与人次
        Integer totalParticipants = activityRepository.sumAllParticipants();
        stats.setTotalParticipants(totalParticipants != null ? totalParticipants : 0);

        // 活动状态统计
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime todayStart = now.toLocalDate().atStartOfDay();
        LocalDateTime todayEnd = todayStart.plusDays(1).minusSeconds(1);

        stats.setOngoingActivities(activityRepository.countByStatus(Activity.ActivityStatus.ONGOING));
        stats.setPendingActivities(activityRepository.countByStatus(Activity.ActivityStatus.PENDING_APPROVAL));
        stats.setCompletedActivities(activityRepository.countByStatus(Activity.ActivityStatus.COMPLETED));
        stats.setTodayActivities(activityRepository.countByStartTimeBetween(todayStart, todayEnd));

        // 审批统计
        stats.setPendingApprovals(activityRepository.countByStatus(Activity.ActivityStatus.PENDING_APPROVAL));
        stats.setPendingFundApprovals((int) fundApplicationRepository.countByStatus(FundApplication.FundStatus.PENDING));

        // 资源统计（简化计算）
        long totalBookings = bookingRepository.count();
        long approvedBookings = bookingRepository.countByStatus("APPROVED");
        stats.setTotalResources(100); // 假设有100个资源
        stats.setOccupiedResources((int) approvedBookings);

        // 资源利用率
        double utilizationRate = totalBookings > 0
            ? (double) approvedBookings / totalBookings * 100
            : 0.0;
        stats.setResourceUtilizationRate(BigDecimal.valueOf(utilizationRate).setScale(1, RoundingMode.HALF_UP));

        // 增长率（与上月对比）
        LocalDateTime monthStart = now.with(TemporalAdjusters.firstDayOfMonth()).withHour(0).withMinute(0);
        LocalDateTime lastMonthStart = monthStart.minusMonths(1);
        LocalDateTime lastMonthEnd = monthStart.minusSeconds(1);

        int thisMonthActivities = activityRepository.countByStartTimeBetween(monthStart, now);
        int lastMonthActivities = activityRepository.countByStartTimeBetween(lastMonthStart, lastMonthEnd);

        if (lastMonthActivities > 0) {
            double growthRate = ((double) thisMonthActivities - lastMonthActivities) / lastMonthActivities * 100;
            stats.setActivityGrowthRate(Math.round(growthRate * 10.0) / 10.0);
        } else {
            stats.setActivityGrowthRate(0.0);
        }

        stats.setParticipantGrowthRate(0.0); // 简化处理

        return stats;
    }

    @Override
    public List<Map<String, Object>> getActivityTrends() {
        List<Map<String, Object>> trends = new ArrayList<>();

        // 生成最近7天的活动数据
        LocalDate today = LocalDate.now();
        for (int i = 6; i >= 0; i--) {
            LocalDate date = today.minusDays(i);
            LocalDateTime start = date.atStartOfDay();
            LocalDateTime end = date.plusDays(1).atStartOfDay().minusSeconds(1);

            int count = activityRepository.countByStartTimeBetween(start, end);

            Map<String, Object> data = new HashMap<>();
            data.put("date", date.toString());
            data.put("count", count);
            trends.add(data);
        }

        return trends;
    }

    @Override
    public List<Map<String, Object>> getClubRankings() {
        List<Map<String, Object>> rankings = new ArrayList<>();

        // 从clubRepository获取所有社团
        clubRepository.findAll().forEach(club -> {
            Map<String, Object> data = new HashMap<>();
            data.put("id", club.getId());
            data.put("name", club.getName());
            data.put("activityCount", activityRepository.countByClubId(club.getId()));
            data.put("memberCount", club.getMemberCount());

            // 计算社团活动参与人次
            Integer participants = activityRepository.sumParticipantsByClubId(club.getId());
            data.put("totalParticipants", participants != null ? participants : 0);

            // 计算活跃度分数（简化：活动数*10 + 参与人次）
            int score = (Integer) data.get("activityCount") * 10 + (Integer) data.get("totalParticipants");
            data.put("score", score);

            rankings.add(data);
        });

        // 按分数排序
        rankings.sort((a, b) -> (Integer) b.get("score") - (Integer) a.get("score"));

        // 只返回前10名
        return rankings.subList(0, Math.min(10, rankings.size()));
    }

    @Override
    public Map<String, Object> getResourceUsage() {
        Map<String, Object> usage = new HashMap<>();

        // 资源类型分布
        Map<String, Integer> typeDistribution = new HashMap<>();
        typeDistribution.put("场地", 40);
        typeDistribution.put("设备", 35);
        typeDistribution.put("会议室", 25);
        usage.put("typeDistribution", typeDistribution);

        // 每日预约数量（最近7天）
        List<Map<String, Object>> dailyBookings = new ArrayList<>();
        LocalDate today = LocalDate.now();
        for (int i = 6; i >= 0; i--) {
            LocalDate date = today.minusDays(i);
            LocalDateTime start = date.atStartOfDay();
            LocalDateTime end = date.plusDays(1).atStartOfDay().minusSeconds(1);

            int count = (int) bookingRepository.countByStartTimeBetween(start, end);

            Map<String, Object> data = new HashMap<>();
            data.put("date", date.toString());
            data.put("count", count);
            dailyBookings.add(data);
        }
        usage.put("dailyBookings", dailyBookings);

        // 资源利用率
        long total = bookingRepository.count();
        long approved = bookingRepository.countByStatus("APPROVED");
        double rate = total > 0 ? (double) approved / total * 100 : 0;
        usage.put("utilizationRate", BigDecimal.valueOf(rate).setScale(1, RoundingMode.HALF_UP));

        return usage;
    }

    @Override
    public Map<String, Integer> getPendingTasks() {
        Map<String, Integer> pendingTasks = new HashMap<>();

        // 待审批活动
        pendingTasks.put("activityApprovals",
            activityRepository.countByStatus(Activity.ActivityStatus.PENDING_APPROVAL));

        // 待审批资金申请
        pendingTasks.put("fundApprovals",
            (int) fundApplicationRepository.countByStatus(FundApplication.FundStatus.PENDING));

        // 待处理资源预约
        pendingTasks.put("resourceBookings",
            (int) bookingRepository.countByStatus("PENDING"));

        // 总待办数
        int total = pendingTasks.values().stream().mapToInt(Integer::intValue).sum();
        pendingTasks.put("total", total);

        return pendingTasks;
    }
}
