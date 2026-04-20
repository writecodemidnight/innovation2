package com.campusclub.dashboard.controller;

import com.campusclub.dashboard.dto.AdminDashboardStatsDTO;
import com.campusclub.dashboard.service.AdminDashboardService;
import com.campusclub.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * 管理端仪表盘控制器
 * 提供系统全局统计数据
 */
@RestController
@RequestMapping("/v1/admin/dashboard")
@RequiredArgsConstructor
@Tag(name = "管理端仪表盘", description = "系统全局数据统计接口")
public class AdminDashboardController {

    private final AdminDashboardService adminDashboardService;

    /**
     * 获取全局统计数据
     */
    @GetMapping("/stats")
    @Operation(summary = "获取全局统计数据", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    public ApiResponse<AdminDashboardStatsDTO> getGlobalStats() {
        AdminDashboardStatsDTO stats = adminDashboardService.getGlobalStats();
        return ApiResponse.success(stats);
    }

    /**
     * 获取活动趋势数据
     */
    @GetMapping("/activity-trends")
    @Operation(summary = "获取活动趋势数据", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    public ApiResponse<List<Map<String, Object>>> getActivityTrends() {
        List<Map<String, Object>> trends = adminDashboardService.getActivityTrends();
        return ApiResponse.success(trends);
    }

    /**
     * 获取社团排行榜
     */
    @GetMapping("/club-rankings")
    @Operation(summary = "获取社团排行榜", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    public ApiResponse<List<Map<String, Object>>> getClubRankings() {
        List<Map<String, Object>> rankings = adminDashboardService.getClubRankings();
        return ApiResponse.success(rankings);
    }

    /**
     * 获取资源使用情况
     */
    @GetMapping("/resource-usage")
    @Operation(summary = "获取资源使用情况", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    public ApiResponse<Map<String, Object>> getResourceUsage() {
        Map<String, Object> usage = adminDashboardService.getResourceUsage();
        return ApiResponse.success(usage);
    }

    /**
     * 获取待办事项统计
     */
    @GetMapping("/pending-tasks")
    @Operation(summary = "获取待办事项统计", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    public ApiResponse<Map<String, Integer>> getPendingTasks() {
        Map<String, Integer> pendingTasks = adminDashboardService.getPendingTasks();
        return ApiResponse.success(pendingTasks);
    }
}
