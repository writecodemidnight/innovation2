package com.campusclub.recommendation.controller;

import com.campusclub.activity.application.dto.ActivityDto;
import com.campusclub.dto.ApiResponse;
import com.campusclub.recommendation.service.RecommendationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/v1/recommendations")
@RequiredArgsConstructor
@Tag(name = "个性推荐", description = "基于K-Means聚类的个性化活动推荐")
public class RecommendationController {

    private final RecommendationService recommendationService;

    /**
     * 获取个性化推荐活动
     */
    @GetMapping("/personalized")
    @SecurityRequirement(name = "bearerAuth")
    @Operation(summary = "个性推荐", description = "基于K-Means聚类算法的个性化活动推荐")
    public ResponseEntity<ApiResponse<List<ActivityDto>>> getPersonalizedRecommendations(
            @AuthenticationPrincipal Long userId) {
        List<ActivityDto> recommendations = recommendationService.getPersonalizedRecommendations(userId);
        return ResponseEntity.ok(ApiResponse.success(recommendations));
    }

    /**
     * 获取热门推荐（默认推荐）
     */
    @GetMapping("/hot")
    @Operation(summary = "热门推荐", description = "获取最热门的活动推荐")
    public ResponseEntity<ApiResponse<List<ActivityDto>>> getHotRecommendations() {
        List<ActivityDto> recommendations = recommendationService.getDefaultRecommendations();
        return ResponseEntity.ok(ApiResponse.success(recommendations));
    }
}
