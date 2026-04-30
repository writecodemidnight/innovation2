package com.campusclub.dashboard.service.impl;

import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.dashboard.dto.ActivityTrendDTO;
import com.campusclub.dashboard.dto.ActivityTypeDistributionDTO;
import com.campusclub.dashboard.dto.ClubDashboardStatsDTO;
import com.campusclub.dashboard.service.DashboardService;
import com.campusclub.resource.domain.repository.ResourceBookingRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.TemporalAdjusters;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j

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
        log.info("获取社团仪表盘统计数据, clubId={}", clubId);
        ClubDashboardStatsDTO stats = new ClubDashboardStatsDTO();

        if (clubId == null) {
            log.warn("clubId 为空，返回默认数据");
            return stats;
        }

        // 本月活动数
        LocalDateTime monthStart = LocalDateTime.now().with(TemporalAdjusters.firstDayOfMonth()).withHour(0).withMinute(0);
        LocalDateTime monthEnd = LocalDateTime.now().with(TemporalAdjusters.lastDayOfMonth()).withHour(23).withMinute(59);
        Integer monthlyActivities = activityRepository.countByClubIdAndStartTimeBetween(clubId, monthStart, monthEnd);
        stats.setMonthlyActivities(monthlyActivities != null ? monthlyActivities : 0);
        log.info("本月活动数: {}", stats.getMonthlyActivities());

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

        // 参与人次 - 只统计已结束的活动
        Integer totalParticipants = activityRepository.sumParticipantsByClubIdAndStatus(clubId, Activity.ActivityStatus.COMPLETED);
        stats.setTotalParticipants(totalParticipants != null ? totalParticipants : 0);
        log.info("参与人次(已结束活动): {}", stats.getTotalParticipants());

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

        log.info("统计数据结果: monthlyActivities={}, totalParticipants={}, completedActivities={}",
                stats.getMonthlyActivities(), stats.getTotalParticipants(), stats.getCompletedActivities());

        return stats;
    }

    @Override
    public ActivityTrendDTO getActivityTrend(Long clubId, LocalDate start, LocalDate end) {
        log.info("获取活动趋势, clubId={}, start={}, end={}", clubId, start, end);

        if (clubId == null) {
            log.warn("clubId 为空，返回空数据");
            return ActivityTrendDTO.builder()
                    .dates(new ArrayList<>())
                    .counts(new ArrayList<>())
                    .build();
        }

        LocalDateTime startTime = start.atStartOfDay();
        LocalDateTime endTime = end.atTime(23, 59, 59);
        log.info("查询时间范围: startTime={}, endTime={}", startTime, endTime);

        // 先查询该社团的所有活动（用于调试）
        List<Activity> allActivities = activityRepository.findByClubId(clubId, org.springframework.data.domain.Pageable.unpaged()).getContent();
        log.info("社团 {} 共有 {} 个活动", clubId, allActivities.size());
        for (Activity a : allActivities) {
            log.info("活动: id={}, title={}, startTime={}, status={}, clubId={}",
                    a.getId(), a.getTitle(), a.getStartTime(), a.getStatus(), a.getClubId());
        }

        // 获取日期范围内的活动统计
        List<Object[]> results = activityRepository.countActivitiesByDate(clubId, startTime, endTime);
        log.info("查询到 {} 条日期统计记录", results.size());
        for (Object[] r : results) {
            log.info("日期统计: date={}, count={}", r[0], r[1]);
        }

        // 构建日期到数量的映射
        Map<LocalDate, Integer> dateCountMap = new HashMap<>();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM-dd");

        for (Object[] result : results) {
            java.sql.Date sqlDate = (java.sql.Date) result[0];
            Long count = (Long) result[1];
            LocalDate date = sqlDate.toLocalDate();
            dateCountMap.put(date, count.intValue());
            log.debug("日期 {} 有 {} 个活动", date, count);
        }

        // 填充整个日期范围（包括没有活动的日期）
        List<String> dates = new ArrayList<>();
        List<Integer> counts = new ArrayList<>();

        LocalDate current = start;
        while (!current.isAfter(end)) {
            dates.add(current.format(formatter));
            counts.add(dateCountMap.getOrDefault(current, 0));
            current = current.plusDays(1);
        }

        log.info("返回趋势数据: dates={}, counts={}", dates, counts);

        return ActivityTrendDTO.builder()
                .dates(dates)
                .counts(counts)
                .build();
    }

    @Override
    public ActivityTypeDistributionDTO getActivityTypeDistribution(Long clubId) {
        log.info("获取活动类型分布, clubId={}", clubId);

        if (clubId == null) {
            log.warn("clubId 为空，返回空数据");
            return ActivityTypeDistributionDTO.builder()
                    .types(new ArrayList<>())
                    .build();
        }

        List<Object[]> results = activityRepository.countActivitiesByType(clubId);
        log.info("查询到 {} 条类型统计记录", results.size());

        List<ActivityTypeDistributionDTO.TypeItem> types = new ArrayList<>();

        // 类型名称映射
        Map<String, String> typeNameMap = new HashMap<>();
        typeNameMap.put("LECTURE", "讲座");
        typeNameMap.put("WORKSHOP", "工作坊");
        typeNameMap.put("COMPETITION", "竞赛");
        typeNameMap.put("SOCIAL", "社交");
        typeNameMap.put("VOLUNTEER", "志愿");
        typeNameMap.put("SPORTS", "体育");
        typeNameMap.put("ENTERTAINMENT", "娱乐");

        for (Object[] result : results) {
            Activity.ActivityType type = (Activity.ActivityType) result[0];
            Long count = (Long) result[1];

            log.debug("类型 {} 有 {} 个活动", type.name(), count);

            types.add(ActivityTypeDistributionDTO.TypeItem.builder()
                    .name(typeNameMap.getOrDefault(type.name(), type.name()))
                    .code(type.name())
                    .value(count.intValue())
                    .build());
        }

        log.info("返回类型分布: {}", types);

        return ActivityTypeDistributionDTO.builder()
                .types(types)
                .build();
    }
}
