package com.campusclub.dashboard.service;

import com.campusclub.dashboard.dto.ClubDashboardStatsDTO;

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
}
