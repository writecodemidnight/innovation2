package com.campusclub.admin.controller;

import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.dto.ApiResponse;
import com.campusclub.fund.domain.entity.FundApplication;
import com.campusclub.fund.repository.FundApplicationRepository;
import com.campusclub.resource.domain.entity.ResourceBooking;
import com.campusclub.resource.domain.repository.ResourceBookingRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 管理员审批历史控制器
 * 查询已审批的历史记录
 */
@RestController
@RequestMapping("/v1/admin/history")
@RequiredArgsConstructor
@Tag(name = "管理端审批历史", description = "已审批事项历史记录查询")
public class AdminHistoryController {

    private final ActivityRepository activityRepository;
    private final ResourceBookingRepository bookingRepository;
    private final FundApplicationRepository fundApplicationRepository;

    /**
     * 获取已审批活动列表（通过APPROVED状态查询）
     */
    @GetMapping("/activities")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取已审批活动列表", description = "获取所有已审批通过的活动")
    public ResponseEntity<ApiResponse<Page<Activity>>> getApprovedActivities(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("updatedAt").descending());
        Page<Activity> activities = activityRepository.findByStatus(Activity.ActivityStatus.APPROVED, pageable);
        return ResponseEntity.ok(ApiResponse.success(activities));
    }

    /**
     * 获取已审批资源预约列表
     */
    @GetMapping("/resource-bookings")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取已审批资源预约列表", description = "获取所有已审批通过的资源预约")
    public ResponseEntity<ApiResponse<List<ResourceBooking>>> getApprovedResourceBookings() {
        List<ResourceBooking> bookings = bookingRepository.findByStatusAndDeletedFalse("APPROVED");
        return ResponseEntity.ok(ApiResponse.success(bookings));
    }

    /**
     * 获取已审批资金申请列表
     */
    @GetMapping("/fund-applications")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取已审批资金申请列表", description = "获取所有已审批（通过/拒绝）的资金申请")
    public ResponseEntity<ApiResponse<List<FundApplication>>> getApprovedFundApplications() {
        // 查询所有非PENDING状态的资金申请
        List<FundApplication> applications = fundApplicationRepository.findByStatusNot(FundApplication.FundStatus.PENDING);
        return ResponseEntity.ok(ApiResponse.success(applications));
    }

    /**
     * 获取审批历史统计
     */
    @GetMapping("/counts")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取审批历史统计", description = "获取各类已审批事项的数量统计")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getHistoryCounts() {
        Map<String, Object> counts = new HashMap<>();

        // 活动统计
        Map<String, Long> activityStats = new HashMap<>();
        activityStats.put("approved", (long) activityRepository.countByStatus(Activity.ActivityStatus.APPROVED));
        activityStats.put("completed", (long) activityRepository.countByStatus(Activity.ActivityStatus.COMPLETED));
        counts.put("activities", activityStats);

        // 资源预约统计
        Map<String, Long> bookingStats = new HashMap<>();
        bookingStats.put("approved", bookingRepository.countByStatus("APPROVED"));
        counts.put("resourceBookings", bookingStats);

        // 资金申请统计
        Map<String, Long> fundStats = new HashMap<>();
        fundStats.put("approved", fundApplicationRepository.countByStatus(FundApplication.FundStatus.APPROVED));
        fundStats.put("rejected", fundApplicationRepository.countByStatus(FundApplication.FundStatus.REJECTED));
        counts.put("fundApplications", fundStats);

        return ResponseEntity.ok(ApiResponse.success(counts));
    }
}
