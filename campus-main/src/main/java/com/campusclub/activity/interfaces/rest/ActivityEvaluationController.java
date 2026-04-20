package com.campusclub.activity.interfaces.rest;

import com.campusclub.activity.application.dto.ActivityEvaluationRequest;
import com.campusclub.activity.application.dto.ActivityEvaluationResponse;
import com.campusclub.activity.application.service.ActivityEvaluationService;
import com.campusclub.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * 活动效果评估控制器
 * 提供活动五维评估接口
 */
@RestController
@RequestMapping("/v1")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "活动评估", description = "活动效果评估相关接口")
public class ActivityEvaluationController {

    private final ActivityEvaluationService evaluationService;

    /**
     * 评估活动效果
     * 调用AHP算法进行五维评估
     */
    @PostMapping("/activities/{id}/evaluate")
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN')")
    @Operation(summary = "评估活动效果", description = "对已完成的活动进行五维效果评估")
    public ResponseEntity<ApiResponse<ActivityEvaluationResponse>> evaluateActivity(
            @PathVariable Long id,
            @Valid @RequestBody ActivityEvaluationRequest request) {

        log.info("收到活动评估请求: activityId={}", id);

        // 确保请求中的activityId与路径参数一致
        request.setActivityId(id);

        ActivityEvaluationResponse response = evaluationService.evaluateActivity(request);

        return ResponseEntity.ok(ApiResponse.success(response));
    }

    /**
     * 获取活动评估结果 - 匹配前端路径 /evaluation/{activityId}/report
     */
    @GetMapping("/evaluation/{activityId}/report")
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN', 'STUDENT')")
    @Operation(summary = "获取活动评估报告", description = "获取活动的五维评估报告和雷达图数据")
    public ResponseEntity<ApiResponse<ActivityEvaluationResponse>> getEvaluationReport(
            @PathVariable Long activityId) {

        log.info("获取活动评估报告: activityId={}", activityId);

        ActivityEvaluationResponse response = evaluationService.getOrCreateEvaluation(activityId);

        return ResponseEntity.ok(ApiResponse.success(response));
    }

    /**
     * 获取活动评估结果（备用路径）
     */
    @GetMapping("/activities/{id}/evaluation")
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN', 'STUDENT')")
    @Operation(summary = "获取活动评估结果", description = "获取活动的五维评估结果")
    public ResponseEntity<ApiResponse<ActivityEvaluationResponse>> getEvaluation(
            @PathVariable Long id) {

        log.info("获取活动评估结果: activityId={}", id);

        ActivityEvaluationResponse response = evaluationService.getOrCreateEvaluation(id);

        return ResponseEntity.ok(ApiResponse.success(response));
    }

    /**
     * 批量评估多个活动
     */
    @PostMapping("/batch-evaluate")
    @PreAuthorize("hasAnyRole('ADMIN', 'CLUB_PRESIDENT')")
    @Operation(summary = "批量评估活动", description = "批量对多个活动进行效果评估")
    public ResponseEntity<ApiResponse<String>> batchEvaluateActivities(
            @RequestBody java.util.List<Long> activityIds) {

        log.info("批量评估活动: count={}", activityIds.size());

        // TODO: 实现批量评估逻辑

        return ResponseEntity.ok(ApiResponse.success("批量评估任务已提交"));
    }
}
