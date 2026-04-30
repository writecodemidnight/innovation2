package com.campusclub.dashboard.service;

import com.campusclub.dashboard.dto.ActivityTrendDTO;
import com.campusclub.dashboard.dto.ActivityTypeDistributionDTO;
import com.campusclub.dashboard.dto.ClubDashboardStatsDTO;

import java.time.LocalDate;

/**
 * 仪表盘服务接口
 */
public interface DashboardService {

    /**
     * 获取社团仪表盘统计数据
     *
     * @param clubId 社团ID
     * @return 统计数据
     */
    ClubDashboardStatsDTO getClubStats(Long clubId);

    /**
     * 获取活动趋势数据
     *
     * @param clubId 社团ID
     * @param start 开始日期
     * @param end 结束日期
     * @return 趋势数据
     */
    ActivityTrendDTO getActivityTrend(Long clubId, LocalDate start, LocalDate end);

    /**
     * 获取活动类型分布
     *
     * @param clubId 社团ID
     * @return 类型分布数据
     */
    ActivityTypeDistributionDTO getActivityTypeDistribution(Long clubId);
}
