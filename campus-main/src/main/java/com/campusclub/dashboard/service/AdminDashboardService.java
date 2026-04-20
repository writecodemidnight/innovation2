package com.campusclub.dashboard.service;

import java.util.List;
import java.util.Map;

import com.campusclub.dashboard.dto.AdminDashboardStatsDTO;

/**
 * 管理端仪表盘服务接口
 */
public interface AdminDashboardService {

    /**
     * 获取全局统计数据
     */
    AdminDashboardStatsDTO getGlobalStats();

    /**
     * 获取活动趋势数据
     */
    List<Map<String, Object>> getActivityTrends();

    /**
     * 获取社团排行榜
     */
    List<Map<String, Object>> getClubRankings();

    /**
     * 获取资源使用情况
     */
    Map<String, Object> getResourceUsage();

    /**
     * 获取待办事项统计
     */
    Map<String, Integer> getPendingTasks();
}
