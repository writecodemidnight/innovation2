package com.campusclub.admin.controller;

import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.dto.ApiResponse;
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

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 管理员审批控制器
 * 集中处理所有待审批事项（活动、资源预约）
 */
@RestController
@RequestMapping("/v1/admin/approvals")
@RequiredArgsConstructor
@Tag(name = "管理端审批", description = "活动、资源预约审批管理接口")
public class AdminApprovalController {

    private final ActivityRepository activityRepository;
    private final ResourceBookingRepository bookingRepository;
    private final com.campusclub.fund.repository.FundApplicationRepository fundApplicationRepository;

    // ==================== 活动审批 ====================

    /**
     * 获取待审批活动列表
     */
    @GetMapping("/activities/pending")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取待审批活动列表", description = "获取所有待审批的活动申请")
    public ResponseEntity<ApiResponse<List<Activity>>> getPendingActivities(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").ascending());
        Page<Activity> activities = activityRepository.findByStatus(Activity.ActivityStatus.PENDING_APPROVAL, pageable);
        return ResponseEntity.ok(ApiResponse.success(activities.getContent()));
    }

    /**
     * 审批通过活动
     */
    @PostMapping("/activities/{id}/approve")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "通过活动审批", description = "管理员通过活动申请")
    public ResponseEntity<ApiResponse<Activity>> approveActivity(
            @PathVariable Long id,
            @RequestBody(required = false) ApprovalRequest request) {
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("活动不存在"));

        activity.setStatus(Activity.ActivityStatus.REGISTERING);
        activity.setUpdatedAt(LocalDateTime.now());
        activityRepository.save(activity);

        return ResponseEntity.ok(ApiResponse.success("活动审批通过", activity));
    }

    /**
     * 审批拒绝活动
     */
    @PostMapping("/activities/{id}/reject")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "拒绝活动审批", description = "管理员拒绝活动申请")
    public ResponseEntity<ApiResponse<Activity>> rejectActivity(
            @PathVariable Long id,
            @RequestBody(required = false) ApprovalRequest request) {
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("活动不存在"));

        activity.setStatus(Activity.ActivityStatus.REJECTED);
        activity.setUpdatedAt(LocalDateTime.now());
        activityRepository.save(activity);

        return ResponseEntity.ok(ApiResponse.success("活动审批已拒绝", activity));
    }

    // ==================== 资源预约审批 ====================

    /**
     * 获取待审批资源预约列表
     */
    @GetMapping("/resource-bookings/pending")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取待审批资源预约列表", description = "获取所有待审批的资源预约申请")
    public ResponseEntity<ApiResponse<List<ResourceBooking>>> getPendingResourceBookings(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").ascending());
        // 使用repository方法查找待审批预约
        List<ResourceBooking> bookings = bookingRepository.findByStatusAndDeletedFalse("PENDING");
        return ResponseEntity.ok(ApiResponse.success(bookings));
    }

    /**
     * 审批通过资源预约
     */
    @PostMapping("/resource-bookings/{id}/approve")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "通过资源预约审批", description = "管理员通过资源预约申请")
    public ResponseEntity<ApiResponse<ResourceBooking>> approveResourceBooking(
            @PathVariable Long id,
            @RequestBody(required = false) ApprovalRequest request) {
        ResourceBooking booking = bookingRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("预约不存在"));

        booking.setStatus("APPROVED");
        booking.setUpdatedAt(LocalDateTime.now());
        bookingRepository.save(booking);

        return ResponseEntity.ok(ApiResponse.success("资源预约审批通过", booking));
    }

    /**
     * 审批拒绝资源预约
     */
    @PostMapping("/resource-bookings/{id}/reject")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "拒绝资源预约审批", description = "管理员拒绝资源预约申请")
    public ResponseEntity<ApiResponse<ResourceBooking>> rejectResourceBooking(
            @PathVariable Long id,
            @RequestBody(required = false) ApprovalRequest request) {
        ResourceBooking booking = bookingRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("预约不存在"));

        booking.setStatus("REJECTED");
        booking.setUpdatedAt(LocalDateTime.now());
        bookingRepository.save(booking);

        return ResponseEntity.ok(ApiResponse.success("资源预约审批已拒绝", booking));
    }

    // ==================== 汇总统计 ====================

    /**
     * 获取各类待审批数量统计
     */
    @GetMapping("/counts")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取待审批数量统计", description = "获取各类待审批事项的数量")
    public ResponseEntity<ApiResponse<Map<String, Long>>> getApprovalCounts() {
        Map<String, Long> counts = new HashMap<>();
        counts.put("activities", (long) activityRepository.countByStatus(Activity.ActivityStatus.PENDING_APPROVAL));
        counts.put("resourceBookings", bookingRepository.countByStatus("PENDING"));
        counts.put("fundApplications", fundApplicationRepository.countByStatus(com.campusclub.fund.domain.entity.FundApplication.FundStatus.PENDING));
        return ResponseEntity.ok(ApiResponse.success(counts));
    }

    /**
     * 审批请求DTO
     */
    public static class ApprovalRequest {
        private String comment;

        public String getComment() {
            return comment;
        }

        public void setComment(String comment) {
            this.comment = comment;
        }
    }
}
