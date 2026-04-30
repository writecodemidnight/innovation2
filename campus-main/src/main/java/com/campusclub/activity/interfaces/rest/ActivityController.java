package com.campusclub.activity.interfaces.rest;

import com.campusclub.activity.application.dto.ActivityCreateRequest;
import com.campusclub.activity.application.dto.ActivityDto;
import com.campusclub.activity.application.dto.ActivityParticipantDto;
import com.campusclub.activity.application.service.ActivityApplicationService;
import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.common.security.UserContext;
import com.campusclub.dto.ApiResponse;
import com.campusclub.recommendation.service.RecommendationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/v1/activities")
@RequiredArgsConstructor
@Tag(name = "活动", description = "活动管理相关接口")
public class ActivityController {

    private final ActivityApplicationService activityService;
    private final RecommendationService recommendationService;

    // GET /api/v1/activities - 活动列表（支持筛选）- 公开
    @GetMapping
    @Operation(summary = "活动列表", description = "获取活动列表，支持按状态、类型、社团筛选")
    public ResponseEntity<ApiResponse<Page<ActivityDto>>> listActivities(
            @RequestParam(required = false) Activity.ActivityStatus status,
            @RequestParam(required = false) Activity.ActivityType type,
            @RequestParam(required = false) Long clubId,
            Pageable pageable) {
        // 如果没有传 clubId，且用户已登录，则使用当前用户的 clubId
        Long effectiveClubId = clubId;
        if (effectiveClubId == null) {
            try {
                effectiveClubId = UserContext.getCurrentClubId();
                log.debug("自动获取当前用户 clubId: {}", effectiveClubId);
            } catch (Exception e) {
                // 用户未登录或没有社团，不传 clubId，返回所有公开活动
                log.debug("无法获取当前用户 clubId，返回所有活动");
            }
        }
        Page<ActivityDto> activities = activityService.listActivities(status, type, effectiveClubId, pageable);
        return ResponseEntity.ok(ApiResponse.success(activities));
    }

    // GET /api/v1/activities/{id} - 活动详情 - 公开
    @GetMapping("/{id}")
    @Operation(summary = "活动详情", description = "获取活动详细信息")
    public ResponseEntity<ApiResponse<ActivityDto>> getActivity(@PathVariable Long id) {
        ActivityDto activity = activityService.getActivity(id);
        return ResponseEntity.ok(ApiResponse.success(activity));
    }

    // POST /api/v1/activities - 创建活动 - CLUB_MEMBER+
    @PostMapping
    @PreAuthorize("hasAnyRole('CLUB_MEMBER', 'CLUB_MANAGER', 'CLUB_PRESIDENT', 'ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "创建活动", description = "创建新活动")
    public ResponseEntity<ApiResponse<ActivityDto>> createActivity(
            @AuthenticationPrincipal Long userId,
            @RequestBody @Valid ActivityCreateRequest request) {
        ActivityDto activity = activityService.createActivity(userId, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(ApiResponse.success("活动创建成功", activity));
    }

    // PUT /api/v1/activities/{id} - 更新活动 - 创建者/MANAGER+
    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('CLUB_MEMBER', 'CLUB_MANAGER', 'CLUB_PRESIDENT', 'ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "更新活动", description = "更新活动信息")
    public ResponseEntity<ApiResponse<ActivityDto>> updateActivity(
            @PathVariable Long id,
            @RequestBody @Valid ActivityCreateRequest request) {
        ActivityDto activity = activityService.updateActivity(id, request);
        return ResponseEntity.ok(ApiResponse.success("活动更新成功", activity));
    }

    // DELETE /api/v1/activities/{id} - 删除活动 - 创建者/MANAGER+
    @DeleteMapping("/{id}")
    @PreAuthorize("hasAnyRole('CLUB_MEMBER', 'CLUB_MANAGER', 'CLUB_PRESIDENT', 'ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "删除活动", description = "删除活动")
    public ResponseEntity<ApiResponse<Void>> deleteActivity(@PathVariable Long id) {
        activityService.deleteActivity(id);
        return ResponseEntity.ok(ApiResponse.success("活动删除成功", null));
    }

    // POST /api/v1/activities/{id}/submit - 提交审批 - 创建者
    @PostMapping("/{id}/submit")
    @PreAuthorize("hasAnyRole('CLUB_MEMBER', 'CLUB_MANAGER', 'CLUB_PRESIDENT', 'ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "提交审批", description = "提交活动审批")
    public ResponseEntity<ApiResponse<Void>> submitForApproval(@PathVariable Long id) {
        activityService.submitForApproval(id);
        return ResponseEntity.ok(ApiResponse.success("活动已提交审批", null));
    }

    // POST /api/v1/activities/{id}/register - 报名活动 - 已登录
    @PostMapping("/{id}/register")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "报名活动", description = "报名参加活动")
    public ResponseEntity<ApiResponse<Void>> registerForActivity(
            @PathVariable Long id,
            @AuthenticationPrincipal Long userId) {
        activityService.registerForActivity(id, userId);
        return ResponseEntity.ok(ApiResponse.success("报名成功", null));
    }

    // POST /api/v1/activities/{id}/cancel - 取消报名 - 已登录
    @PostMapping("/{id}/cancel")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "取消报名", description = "取消活动报名")
    public ResponseEntity<ApiResponse<Void>> cancelRegistration(
            @PathVariable Long id,
            @AuthenticationPrincipal Long userId) {
        activityService.cancelRegistration(id, userId);
        return ResponseEntity.ok(ApiResponse.success("取消报名成功", null));
    }

    // POST /api/v1/activities/{id}/check-in - 活动签到 - 已登录
    @PostMapping("/{id}/check-in")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "活动签到", description = "活动签到")
    public ResponseEntity<ApiResponse<Void>> checkIn(
            @PathVariable Long id,
            @AuthenticationPrincipal Long userId) {
        activityService.checkIn(id, userId);
        return ResponseEntity.ok(ApiResponse.success("签到成功", null));
    }

    // GET /api/v1/activities/{id}/participants - 参与者列表 - MANAGER+
    @GetMapping("/{id}/participants")
    @PreAuthorize("hasAnyRole('CLUB_MANAGER', 'CLUB_PRESIDENT', 'ADMIN', 'SUPER_ADMIN')")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "参与者列表", description = "获取活动参与者列表")
    public ResponseEntity<ApiResponse<List<ActivityParticipantDto>>> listParticipants(
            @PathVariable Long id) {
        List<ActivityParticipantDto> participants = activityService.listParticipants(id);
        return ResponseEntity.ok(ApiResponse.success(participants));
    }

    // GET /api/v1/activities/my - 我的活动 - 已登录
    @GetMapping("/my")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "我的活动", description = "获取我报名的活动列表")
    public ResponseEntity<ApiResponse<List<ActivityDto>>> listMyActivities(
            @AuthenticationPrincipal Long userId) {
        List<ActivityDto> activities = activityService.listMyActivities(userId);
        return ResponseEntity.ok(ApiResponse.success(activities));
    }

    // GET /api/v1/activities/recommend - 推荐活动 - 已登录（用于个性化推荐）
    @GetMapping("/recommend")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "个性推荐", description = "基于K-Means聚类算法的个性化活动推荐")
    public ResponseEntity<ApiResponse<List<ActivityDto>>> getRecommendedActivities(
            @AuthenticationPrincipal Long userId) {
        List<ActivityDto> activities = recommendationService.getPersonalizedRecommendations(userId);
        return ResponseEntity.ok(ApiResponse.success(activities));
    }

    // GET /api/v1/activities/hot - 热门活动 - 公开
    @GetMapping("/hot")
    @Operation(summary = "热门活动", description = "获取热门活动列表")
    public ResponseEntity<ApiResponse<List<ActivityDto>>> getHotActivities() {
        List<ActivityDto> activities = activityService.getHotActivities();
        return ResponseEntity.ok(ApiResponse.success(activities));
    }

    // GET /api/v1/activities/upcoming - 即将开始的活动 - 公开
    @GetMapping("/upcoming")
    @Operation(summary = "即将开始的活动", description = "获取未来7天内即将开始的活动")
    public ResponseEntity<ApiResponse<List<ActivityDto>>> getUpcomingActivities() {
        List<ActivityDto> activities = activityService.getUpcomingActivities();
        return ResponseEntity.ok(ApiResponse.success(activities));
    }
}
