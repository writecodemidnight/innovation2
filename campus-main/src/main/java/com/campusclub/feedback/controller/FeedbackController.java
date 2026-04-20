package com.campusclub.feedback.controller;

import com.campusclub.common.security.UserContext;
import com.campusclub.dto.ApiResponse;
import com.campusclub.feedback.dto.CreateFeedbackRequest;
import com.campusclub.feedback.dto.FeedbackDTO;
import com.campusclub.feedback.dto.FeedbackStatsDTO;
import com.campusclub.feedback.service.FeedbackService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * 反馈评价控制器
 */
@RestController
@RequestMapping("/v1/feedback")
@RequiredArgsConstructor
@Tag(name = "反馈评价", description = "活动反馈评价相关接口")
public class FeedbackController {

    private final FeedbackService feedbackService;

    /**
     * 创建反馈评价
     */
    @PostMapping
    @Operation(summary = "创建反馈评价", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('STUDENT', 'CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<FeedbackDTO> createFeedback(@Valid @RequestBody CreateFeedbackRequest request) {
        Long userId = UserContext.getCurrentUserId();
        FeedbackDTO result = feedbackService.createFeedback(request, userId);
        return ApiResponse.success("评价成功", result);
    }

    /**
     * 获取反馈详情
     */
    @GetMapping("/{id}")
    @Operation(summary = "获取反馈详情", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('STUDENT', 'CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN')")
    public ApiResponse<FeedbackDTO> getFeedback(@PathVariable Long id) {
        FeedbackDTO result = feedbackService.getFeedback(id);
        return ApiResponse.success(result);
    }

    /**
     * 获取活动的反馈列表
     */
    @GetMapping("/activity/{activityId}")
    @Operation(summary = "获取活动的反馈列表", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('STUDENT', 'CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN')")
    public ApiResponse<Page<FeedbackDTO>> getFeedbacksByActivity(
            @PathVariable Long activityId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<FeedbackDTO> result = feedbackService.getFeedbacksByActivity(activityId, pageable);
        return ApiResponse.success(result);
    }

    /**
     * 获取我的反馈列表
     */
    @GetMapping("/my")
    @Operation(summary = "获取我的反馈列表", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('STUDENT', 'CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<Page<FeedbackDTO>> getMyFeedbacks(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Long userId = UserContext.getCurrentUserId();
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<FeedbackDTO> result = feedbackService.getFeedbacksByUser(userId, pageable);
        return ApiResponse.success(result);
    }

    /**
     * 获取反馈统计
     */
    @GetMapping("/activity/{activityId}/stats")
    @Operation(summary = "获取活动反馈统计", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('STUDENT', 'CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN')")
    public ApiResponse<FeedbackStatsDTO> getFeedbackStats(@PathVariable Long activityId) {
        FeedbackStatsDTO result = feedbackService.getFeedbackStats(activityId);
        return ApiResponse.success(result);
    }

    /**
     * 更新反馈
     */
    @PutMapping("/{id}")
    @Operation(summary = "更新反馈", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('STUDENT', 'CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<FeedbackDTO> updateFeedback(
            @PathVariable Long id,
            @Valid @RequestBody CreateFeedbackRequest request) {
        Long userId = UserContext.getCurrentUserId();
        FeedbackDTO result = feedbackService.updateFeedback(id, request, userId);
        return ApiResponse.success("更新成功", result);
    }

    /**
     * 删除反馈
     */
    @DeleteMapping("/{id}")
    @Operation(summary = "删除反馈", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('STUDENT', 'CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<Void> deleteFeedback(@PathVariable Long id) {
        Long userId = UserContext.getCurrentUserId();
        feedbackService.deleteFeedback(id, userId);
        return ApiResponse.success("删除成功", null);
    }

    /**
     * 检查是否已评价
     */
    @GetMapping("/activity/{activityId}/has-feedback")
    @Operation(summary = "检查用户是否已评价活动", security = @SecurityRequirement(name = "bearerAuth"))
    @PreAuthorize("hasAnyRole('STUDENT', 'CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<Boolean> hasFeedback(@PathVariable Long activityId) {
        Long userId = UserContext.getCurrentUserId();
        boolean result = feedbackService.hasFeedback(activityId, userId);
        return ApiResponse.success(result);
    }
}
