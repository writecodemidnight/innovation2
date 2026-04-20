package com.campusclub.activity.application.service;

import com.campusclub.activity.application.dto.ActivityEvaluationRequest;
import com.campusclub.activity.application.dto.ActivityEvaluationResponse;
import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.common.exception.BusinessException;
import com.campusclub.dto.AlgorithmRequest;
import com.campusclub.dto.AlgorithmResponse;
import com.campusclub.service.AlgorithmService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.HashMap;
import java.util.Map;

/**
 * 活动效果评估服务
 * 调用Python算法服务进行AHP评估
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ActivityEvaluationService {

    private final AlgorithmService algorithmService;
    private final ActivityRepository activityRepository;

    // AHP权重配置（与Python算法服务保持一致）
    private static final Map<String, BigDecimal> DEFAULT_WEIGHTS = new HashMap<>() {{
        put("参与度", new BigDecimal("0.32"));
        put("教育性", new BigDecimal("0.18"));
        put("创新性", new BigDecimal("0.15"));
        put("影响力", new BigDecimal("0.22"));
        put("可持续性", new BigDecimal("0.13"));
    }};

    /**
     * 评估活动效果
     * 调用AHP算法服务进行五维评估
     */
    public ActivityEvaluationResponse evaluateActivity(ActivityEvaluationRequest request) {
        log.info("开始评估活动: {}", request.getActivityId());

        // 1. 验证活动存在
        Activity activity = activityRepository.findById(request.getActivityId())
                .orElseThrow(() -> new BusinessException("活动不存在", HttpStatus.NOT_FOUND));

        // 2. 构建AHP算法请求
        Map<String, Object> scores = new HashMap<>();
        scores.put("参与度", getScoreOrDefault(request.getEngagementScore()));
        scores.put("教育性", getScoreOrDefault(request.getEducationalScore()));
        scores.put("创新性", getScoreOrDefault(request.getInnovationScore()));
        scores.put("影响力", getScoreOrDefault(request.getImpactScore()));
        scores.put("可持续性", getScoreOrDefault(request.getSustainabilityScore()));

        Map<String, Object> parameters = new HashMap<>();
        parameters.put("scores", scores);
        if (request.getExtraData() != null) {
            parameters.putAll(request.getExtraData());
        }

        AlgorithmRequest algorithmRequest = AlgorithmRequest.builder()
                .algorithmType("AHP")
                .parameters(parameters)
                .build();

        // 3. 调用算法服务
        AlgorithmResponse algorithmResponse = algorithmService.executeWithRetry(algorithmRequest);

        // 4. 构建响应
        return buildEvaluationResponse(activity, algorithmResponse);
    }

    /**
     * 获取活动评估结果
     * 如果活动已有评估结果，直接返回；否则进行评估
     */
    public ActivityEvaluationResponse getOrCreateEvaluation(Long activityId) {
        // 暂时直接进行评估（后续可从缓存或数据库读取）
        Activity activity = activityRepository.findById(activityId)
                .orElseThrow(() -> new BusinessException("活动不存在", HttpStatus.NOT_FOUND));

        // 如果活动状态不是已完成，返回空或提示
        if (activity.getStatus() != Activity.ActivityStatus.COMPLETED) {
            throw new BusinessException("活动尚未完成，无法进行评估", HttpStatus.BAD_REQUEST);
        }

        // 使用模拟数据进行评估（实际应从活动参与数据计算）
        ActivityEvaluationRequest request = ActivityEvaluationRequest.builder()
                .activityId(activityId)
                .engagementScore(new BigDecimal("85"))
                .educationalScore(new BigDecimal("78"))
                .innovationScore(new BigDecimal("90"))
                .impactScore(new BigDecimal("82"))
                .sustainabilityScore(new BigDecimal("75"))
                .build();

        return evaluateActivity(request);
    }

    private Double getScoreOrDefault(Object score) {
        if (score == null) return 50.0;
        if (score instanceof Number) return ((Number) score).doubleValue();
        return 50.0;
    }

    @SuppressWarnings("unchecked")
    private ActivityEvaluationResponse buildEvaluationResponse(
            Activity activity, AlgorithmResponse algorithmResponse) {

        Map<String, Object> result = algorithmResponse.getResult();

        // 解析算法返回结果
        BigDecimal totalScore = BigDecimal.valueOf((Double) result.get("total_score"))
                .setScale(2, RoundingMode.HALF_UP);

        Map<String, Object> dimensionScores = (Map<String, Object>) result.get("dimension_scores");
        Map<String, Object> contributionsMap = (Map<String, Object>) result.get("contributions");
        Map<String, Object> weightsMap = (Map<String, Object>) result.get("weights");

        Double consistencyRatio = (Double) result.get("consistency_ratio");
        Boolean consistencyPassed = (Boolean) result.get("consistency_check_passed");

        // 构建权重Map
        Map<String, BigDecimal> weights = new HashMap<>();
        weightsMap.forEach((k, v) -> weights.put(k, new BigDecimal(v.toString())));

        // 构建贡献度Map
        Map<String, BigDecimal> contributions = new HashMap<>();
        contributionsMap.forEach((k, v) -> contributions.put(k, new BigDecimal(v.toString())));

        // 确定评估等级
        String evaluationLevel = determineEvaluationLevel(totalScore);

        // 生成改进建议
        String suggestions = generateSuggestions(contributions);

        return ActivityEvaluationResponse.builder()
                .activityId(activity.getId())
                .activityTitle(activity.getTitle())
                .totalScore(totalScore)
                .engagementScore(BigDecimal.valueOf(getScoreOrDefault(dimensionScores.get("参与度"))))
                .educationalScore(BigDecimal.valueOf(getScoreOrDefault(dimensionScores.get("教育性"))))
                .innovationScore(BigDecimal.valueOf(getScoreOrDefault(dimensionScores.get("创新性"))))
                .impactScore(BigDecimal.valueOf(getScoreOrDefault(dimensionScores.get("影响力"))))
                .sustainabilityScore(BigDecimal.valueOf(getScoreOrDefault(dimensionScores.get("可持续性"))))
                .weights(weights)
                .contributions(contributions)
                .consistencyCheckPassed(consistencyPassed)
                .consistencyRatio(consistencyRatio)
                .evaluationLevel(evaluationLevel)
                .suggestions(suggestions)
                .processingTimeMs(algorithmResponse.getProcessingTimeMs())
                .build();
    }

    private String determineEvaluationLevel(BigDecimal totalScore) {
        if (totalScore.compareTo(new BigDecimal("90")) >= 0) {
            return "优秀";
        } else if (totalScore.compareTo(new BigDecimal("80")) >= 0) {
            return "良好";
        } else if (totalScore.compareTo(new BigDecimal("70")) >= 0) {
            return "中等";
        } else if (totalScore.compareTo(new BigDecimal("60")) >= 0) {
            return "及格";
        } else {
            return "需改进";
        }
    }

    private String generateSuggestions(Map<String, BigDecimal> contributions) {
        // 找出得分最低的维度
        String lowestDimension = contributions.entrySet().stream()
                .min(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("");

        return switch (lowestDimension) {
            case "参与度" -> "建议增加互动环节，提高学生参与积极性";
            case "教育性" -> "建议加强知识传递，增加学习价值";
            case "创新性" -> "建议尝试新颖的活动形式和内容";
            case "影响力" -> "建议加强宣传推广，扩大活动影响范围";
            case "可持续性" -> "建议建立长效机制，确保活动持续开展";
            default -> "请继续保持，活动整体表现良好";
        };
    }
}
