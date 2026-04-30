package com.campusclub.dashboard.controller;

import com.campusclub.common.security.UserContext;
import com.campusclub.dashboard.dto.ActivityTrendDTO;
import com.campusclub.dashboard.dto.ActivityTypeDistributionDTO;
import com.campusclub.dashboard.dto.ClubDashboardStatsDTO;
import com.campusclub.dashboard.service.DashboardService;
import com.campusclub.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;

/**
 * 仪表盘控制器
 */
@RestController
@RequestMapping("/v1/dashboard")
@Slf4j
@RequiredArgsConstructor
@Tag(name = "仪表盘", description = "数据统计和概览接口")
public class DashboardController {

    private final DashboardService dashboardService;

    /**
     * 获取社团仪表盘统计数据
     */
    @GetMapping("/stats")
    @Operation(summary = "获取社团仪表盘统计数据", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("isAuthenticated()")
    public ApiResponse<ClubDashboardStatsDTO> getClubStats() {
        try {
            Long clubId = UserContext.getCurrentClubId();
            log.info("[DashboardController] 获取统计数据, clubId={}", clubId);
            ClubDashboardStatsDTO stats = dashboardService.getClubStats(clubId);
            log.info("[DashboardController] 返回统计数据: {}", stats);
            return ApiResponse.success(stats);
        } catch (Exception e) {
            log.error("[DashboardController] 获取统计数据失败", e);
            // 如果没有关联社团（如管理员），返回默认数据
            ClubDashboardStatsDTO defaultStats = new ClubDashboardStatsDTO();
            defaultStats.setMonthlyActivities(0);
            defaultStats.setMonthlyGrowthRate(0.0);
            defaultStats.setTotalParticipants(0);
            defaultStats.setAverageRating(new java.math.BigDecimal("0.0"));
            defaultStats.setResourceUtilizationRate(0.0);
            defaultStats.setPendingApprovals(0);
            defaultStats.setOngoingActivities(0);
            defaultStats.setCompletedActivities(0);
            return ApiResponse.success(defaultStats);
        }
    }

    /**
     * 获取社团仪表盘概览数据（与stats相同，用于前端兼容）
     */
    @GetMapping("/overview")
    @Operation(summary = "获取社团仪表盘概览数据", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN', 'SUPER_ADMIN')")
    public ApiResponse<ClubDashboardStatsDTO> getClubOverview() {
        return getClubStats();
    }

    /**
     * 获取活动趋势数据
     */
    @GetMapping("/activity-trends")
    @Operation(summary = "获取活动趋势数据", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("isAuthenticated()")
    public ApiResponse<ActivityTrendDTO> getActivityTrends(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate end) {
        try {
            Long clubId = UserContext.getCurrentClubId();
            ActivityTrendDTO trend = dashboardService.getActivityTrend(clubId, start, end);
            return ApiResponse.success(trend);
        } catch (Exception e) {
            // 如果没有关联社团，返回空数据
            return ApiResponse.success(ActivityTrendDTO.builder()
                    .dates(new java.util.ArrayList<>())
                    .counts(new java.util.ArrayList<>())
                    .build());
        }
    }

    /**
     * 获取活动类型分布
     */
    @GetMapping("/activity-types")
    @Operation(summary = "获取活动类型分布", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("isAuthenticated()")
    public ApiResponse<ActivityTypeDistributionDTO> getActivityTypeDistribution() {
        try {
            Long clubId = UserContext.getCurrentClubId();
            ActivityTypeDistributionDTO distribution = dashboardService.getActivityTypeDistribution(clubId);
            return ApiResponse.success(distribution);
        } catch (Exception e) {
            // 如果没有关联社团，返回空数据
            return ApiResponse.success(ActivityTypeDistributionDTO.builder()
                    .types(new java.util.ArrayList<>())
                    .build());
        }
    }
}
