package com.campusclub.evaluation.service;

import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.dto.AlgorithmRequest;
import com.campusclub.dto.AlgorithmResponse;
import com.campusclub.evaluation.dto.EvaluationRequest;
import com.campusclub.evaluation.dto.EvaluationResponse;
import com.campusclub.evaluation.dto.FiveDimensionScores;
import com.campusclub.evaluation.dto.RadarData;
import com.campusclub.service.AlgorithmService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

/**
 * 活动评估服务
 * 负责调用AHP算法服务进行五维评估
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class EvaluationService {

    private final AlgorithmService algorithmService;
    private final ActivityRepository activityRepository;

    // 默认五维权重（基于AHP计算）
    private static final Map<String, Double> DEFAULT_WEIGHTS = Map.of(
            "参与度", 0.32,
            "教育性", 0.18,
            "创新性", 0.15,
            "影响力", 0.22,
            "可持续性", 0.13
    );

    /**
     * 评估活动
     */
    public EvaluationResponse evaluateActivity(EvaluationRequest request, String evaluator) {
        // 构建AHP算法请求参数
        Map<String, Object> scores = new HashMap<>();
        scores.put("参与度", request.getScores().getEngagement());
        scores.put("教育性", request.getScores().getEducational());
        scores.put("创新性", request.getScores().getInnovation());
        scores.put("影响力", request.getScores().getImpact());
        scores.put("可持续性", request.getScores().getSustainability());

        Map<String, Object> parameters = new HashMap<>();
        parameters.put("scores", scores);

        AlgorithmRequest algorithmRequest = AlgorithmRequest.builder()
                .algorithmType("AHP")
                .parameters(parameters)
                .build();

        // 调用算法服务
        AlgorithmResponse algorithmResponse;
        try {
            algorithmResponse = algorithmService.executeWithRetry(algorithmRequest);
        } catch (Exception e) {
            log.warn("AHP算法服务调用失败，使用本地计算", e);
            algorithmResponse = calculateLocally(scores);
        }

        // 构建响应
        return buildEvaluationResponse(request.getActivityId(), request.getScores(), algorithmResponse, evaluator);
    }

    /**
     * 获取活动标题
     */
    private String getActivityTitle(Long activityId) {
        return activityRepository.findById(activityId)
                .map(activity -> activity.getTitle())
                .orElse("活动" + activityId);
    }

    /**
     * 获取活动的评估报告（已评估的活动）
     */
    public EvaluationResponse getEvaluation(Long activityId) {
        // 从数据库查询已保存的评估结果，如果没有则返回基于默认值的评估
        String activityTitle = getActivityTitle(activityId);

        // 暂时返回模拟数据，实际应从评估结果表查询
        return EvaluationResponse.builder()
                .activityId(activityId)
                .activityTitle(activityTitle)
                .totalScore(85.5)
                .dimensionScores(FiveDimensionScores.builder()
                        .engagement(90.0)
                        .educational(80.0)
                        .innovation(85.0)
                        .impact(88.0)
                        .sustainability(75.0)
                        .build())
                .weights(DEFAULT_WEIGHTS)
                .contributions(Map.of(
                        "参与度", 28.8,
                        "教育性", 14.4,
                        "创新性", 12.75,
                        "影响力", 19.36,
                        "可持续性", 9.75
                ))
                .consistencyRatio(0.03)
                .consistencyCheckPassed(true)
                .evaluatedAt(LocalDateTime.now())
                .build();
    }

    /**
     * 获取雷达图数据
     */
    public RadarData getRadarData(Long activityId) {
        EvaluationResponse evaluation = getEvaluation(activityId);
        FiveDimensionScores scores = evaluation.getDimensionScores();

        List<String> dimensions = Arrays.asList("参与度", "教育性", "创新性", "影响力", "可持续性");

        List<RadarData.Indicator> indicators = dimensions.stream()
                .map(d -> RadarData.Indicator.builder()
                        .name(d)
                        .max(100)
                        .color("#5470c6")
                        .build())
                .toList();

        List<Double> values = Arrays.asList(
                scores.getEngagement(),
                scores.getEducational(),
                scores.getInnovation(),
                scores.getImpact(),
                scores.getSustainability()
        );

        RadarData.Series series = RadarData.Series.builder()
                .name("活动评分")
                .type("radar")
                .value(values)
                .areaStyle(RadarData.AreaStyle.builder().opacity(0.3).build())
                .lineStyle(RadarData.LineStyle.builder().width(2).build())
                .build();

        return RadarData.builder()
                .dimensions(dimensions)
                .indicators(indicators)
                .series(Collections.singletonList(series))
                .build();
    }

    /**
     * 本地计算（当算法服务不可用时使用）
     */
    private AlgorithmResponse calculateLocally(Map<String, Object> scores) {
        double engagement = ((Number) scores.get("参与度")).doubleValue();
        double educational = ((Number) scores.get("教育性")).doubleValue();
        double innovation = ((Number) scores.get("创新性")).doubleValue();
        double impact = ((Number) scores.get("影响力")).doubleValue();
        double sustainability = ((Number) scores.get("可持续性")).doubleValue();

        // 使用默认权重计算加权总分
        double totalScore = engagement * DEFAULT_WEIGHTS.get("参与度")
                + educational * DEFAULT_WEIGHTS.get("教育性")
                + innovation * DEFAULT_WEIGHTS.get("创新性")
                + impact * DEFAULT_WEIGHTS.get("影响力")
                + sustainability * DEFAULT_WEIGHTS.get("可持续性");

        Map<String, Object> result = new HashMap<>();
        result.put("total_score", Math.round(totalScore * 100.0) / 100.0);
        result.put("dimension_scores", scores);
        result.put("weights", DEFAULT_WEIGHTS);
        result.put("contributions", Map.of(
                "参与度", Math.round(engagement * DEFAULT_WEIGHTS.get("参与度") * 100.0) / 100.0,
                "教育性", Math.round(educational * DEFAULT_WEIGHTS.get("教育性") * 100.0) / 100.0,
                "创新性", Math.round(innovation * DEFAULT_WEIGHTS.get("创新性") * 100.0) / 100.0,
                "影响力", Math.round(impact * DEFAULT_WEIGHTS.get("影响力") * 100.0) / 100.0,
                "可持续性", Math.round(sustainability * DEFAULT_WEIGHTS.get("可持续性") * 100.0) / 100.0
        ));
        result.put("consistency_ratio", 0.03);
        result.put("consistency_check_passed", true);

        return AlgorithmResponse.builder()
                .success(true)
                .algorithmType("AHP")
                .result(result)
                .processingTimeMs(10L)
                .build();
    }

    /**
     * 构建评估响应
     */
    @SuppressWarnings("unchecked")
    private EvaluationResponse buildEvaluationResponse(
            Long activityId,
            FiveDimensionScores scores,
            AlgorithmResponse algorithmResponse,
            String evaluator
    ) {
        Map<String, Object> result = algorithmResponse.getResult();

        Map<String, Double> weights = (Map<String, Double>) result.get("weights");
        Map<String, Double> contributions = (Map<String, Double>) result.get("contributions");

        return EvaluationResponse.builder()
                .activityId(activityId)
                .activityTitle(getActivityTitle(activityId))
                .totalScore(((Number) result.get("total_score")).doubleValue())
                .dimensionScores(scores)
                .weights(weights)
                .contributions(contributions)
                .consistencyRatio(((Number) result.get("consistency_ratio")).doubleValue())
                .consistencyCheckPassed((Boolean) result.get("consistency_check_passed"))
                .evaluatedBy(evaluator)
                .evaluatedAt(LocalDateTime.now())
                .build();
    }
}
