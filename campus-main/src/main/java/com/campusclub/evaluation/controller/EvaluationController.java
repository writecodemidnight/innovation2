package com.campusclub.evaluation.controller;

import com.campusclub.dto.ApiResponse;
import com.campusclub.evaluation.dto.EvaluationRequest;
import com.campusclub.evaluation.dto.EvaluationResponse;
import com.campusclub.evaluation.dto.RadarData;
import com.campusclub.evaluation.service.EvaluationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

/**
 * 活动评估控制器
 */
@RestController
@RequestMapping("/v1/activities/{activityId}/evaluation")
@RequiredArgsConstructor
@Slf4j
public class EvaluationController {

    private final EvaluationService evaluationService;

    /**
     * 提交活动评估
     */
    @PostMapping
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN')")
    public ApiResponse<EvaluationResponse> evaluateActivity(
            @PathVariable Long activityId,
            @Valid @RequestBody EvaluationRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {
        try {
            // 确保路径参数和请求体中的活动ID一致
            if (!activityId.equals(request.getActivityId())) {
                return ApiResponse.error("VALIDATION_ERROR", "活动ID不匹配");
            }

            String evaluator = userDetails != null ? userDetails.getUsername() : "system";
            EvaluationResponse response = evaluationService.evaluateActivity(request, evaluator);
            return ApiResponse.success("评估成功", response);
        } catch (Exception e) {
            log.error("活动评估失败", e);
            return ApiResponse.error("ERROR", e.getMessage());
        }
    }

    /**
     * 获取活动评估报告
     */
    @GetMapping
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN')")
    public ApiResponse<EvaluationResponse> getEvaluation(
            @PathVariable Long activityId) {
        try {
            EvaluationResponse response = evaluationService.getEvaluation(activityId);
            return ApiResponse.success(response);
        } catch (Exception e) {
            log.error("获取评估报告失败", e);
            return ApiResponse.error("ERROR", e.getMessage());
        }
    }

    /**
     * 获取雷达图数据
     */
    @GetMapping("/radar")
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER', 'ADMIN')")
    public ApiResponse<RadarData> getRadarData(
            @PathVariable Long activityId) {
        try {
            RadarData radarData = evaluationService.getRadarData(activityId);
            return ApiResponse.success(radarData);
        } catch (Exception e) {
            log.error("获取雷达图数据失败", e);
            return ApiResponse.error("ERROR", e.getMessage());
        }
    }
}
