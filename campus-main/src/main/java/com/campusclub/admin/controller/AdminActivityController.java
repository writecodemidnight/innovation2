package com.campusclub.admin.controller;

import com.campusclub.activity.application.dto.ActivityDto;
import com.campusclub.activity.application.service.ActivityApplicationService;
import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.dto.ApiResponse;
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

/**
 * 管理员活动管理控制器
 */
@RestController
@RequestMapping("/v1/admin/activities")
@RequiredArgsConstructor
@Tag(name = "管理端活动管理", description = "管理员活动管理接口")
public class AdminActivityController {

    private final ActivityRepository activityRepository;
    private final ActivityApplicationService activityApplicationService;
    private final com.campusclub.activity.application.mapper.ActivityMapper activityMapper;

    /**
     * 获取活动列表
     */
    @GetMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取活动列表", description = "管理员获取所有活动列表，支持筛选和搜索")
    public ResponseEntity<ApiResponse<Page<ActivityDto>>> getActivities(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Activity.ActivityStatus status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<ActivityDto> activities;

        Page<Activity> activityPage;
        if (keyword != null && !keyword.isEmpty() && status != null) {
            activityPage = activityRepository.findByStatusAndTitleContainingIgnoreCaseAndDeletedFalse(status, keyword, pageable);
        } else if (keyword != null && !keyword.isEmpty()) {
            activityPage = activityRepository.findByTitleContainingIgnoreCaseAndDeletedFalse(keyword, pageable);
        } else if (status != null) {
            activityPage = activityRepository.findByStatusAndDeletedFalse(status, pageable);
        } else {
            activityPage = activityRepository.findAllActive(pageable);
        }
        activities = activityPage.map(activityMapper::toDto);

        return ResponseEntity.ok(ApiResponse.success(activities));
    }

    /**
     * 删除活动
     */
    @DeleteMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "删除活动", description = "管理员删除活动（仅允许删除已结束或已取消的活动）")
    public ResponseEntity<ApiResponse<Void>> deleteActivity(@PathVariable Long id) {
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("活动不存在"));

        // 只允许删除已结束或已取消的活动
        if (activity.getStatus() != Activity.ActivityStatus.COMPLETED
                && activity.getStatus() != Activity.ActivityStatus.CANCELLED) {
            throw new RuntimeException("只能删除已结束或已取消的活动");
        }

        activity.setDeleted(true);
        activityRepository.save(activity);

        return ResponseEntity.ok(ApiResponse.success("活动已删除", null));
    }

    /**
     * 结束活动（管理员可在任何时刻结束活动）
     */
    @PostMapping("/{id}/end")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "结束活动", description = "管理员结束活动（可在任何时刻执行，将状态改为已结束）")
    public ResponseEntity<ApiResponse<Void>> endActivity(@PathVariable Long id) {
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("活动不存在"));

        // 已结束或已取消的活动无需再次结束
        if (activity.getStatus() == Activity.ActivityStatus.COMPLETED
                || activity.getStatus() == Activity.ActivityStatus.CANCELLED) {
            throw new RuntimeException("活动已结束或已取消，无需重复操作");
        }

        activity.setStatus(Activity.ActivityStatus.COMPLETED);
        activity.setUpdatedAt(LocalDateTime.now());
        activityRepository.save(activity);

        return ResponseEntity.ok(ApiResponse.success("活动已结束", null));
    }

    /**
     * 取消活动
     */
    @PostMapping("/{id}/cancel")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "取消活动", description = "管理员取消活动")
    public ResponseEntity<ApiResponse<Void>> cancelActivity(@PathVariable Long id) {
        Activity activity = activityRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("活动不存在"));

        // 已结束或已取消的活动无法取消
        if (activity.getStatus() == Activity.ActivityStatus.COMPLETED
                || activity.getStatus() == Activity.ActivityStatus.CANCELLED) {
            throw new RuntimeException("活动已结束或已取消，无法执行取消操作");
        }

        activity.setStatus(Activity.ActivityStatus.CANCELLED);
        activity.setUpdatedAt(LocalDateTime.now());
        activityRepository.save(activity);

        return ResponseEntity.ok(ApiResponse.success("活动已取消", null));
    }

    /**
     * 获取活动详情
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "获取活动详情", description = "管理员获取活动详细信息")
    public ResponseEntity<ApiResponse<ActivityDto>> getActivityDetail(@PathVariable Long id) {
        ActivityDto activity = activityApplicationService.getActivity(id);
        return ResponseEntity.ok(ApiResponse.success(activity));
    }
}
