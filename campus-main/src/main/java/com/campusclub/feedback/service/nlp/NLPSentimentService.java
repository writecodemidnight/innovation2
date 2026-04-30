package com.campusclub.feedback.service.nlp;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * NLP情感分析服务
 * 调用Python算法服务的NLP API进行情感分析
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class NLPSentimentService {

    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    /**
     * 单条文本情感分析
     */
    public SentimentResult analyzeSentiment(String text) {
        try {
            String url = aiServiceUrl + "/api/v3/ml/nlp/sentiment";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            Map<String, Object> request = new HashMap<>();
            request.put("text", text);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);

            var response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                new ParameterizedTypeReference<Map<String, Object>>() {}
            );

            if (response.getBody() != null && Boolean.TRUE.equals(response.getBody().get("success"))) {
                return mapToSentimentResult(response.getBody());
            }
        } catch (Exception e) {
            log.error("NLP情感分析失败: {}", e.getMessage());
        }

        // 降级处理：返回中性结果
        return SentimentResult.builder()
            .sentimentScore(0.5)
            .sentimentLevel("中性")
            .confidence(0.5)
            .build();
    }

    /**
     * 批量情感分析
     */
    public BatchSentimentResult analyzeSentimentBatch(List<String> texts) {
        try {
            String url = aiServiceUrl + "/api/v3/ml/nlp/sentiment/batch";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            Map<String, Object> request = new HashMap<>();
            request.put("texts", texts);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);

            var response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                new ParameterizedTypeReference<Map<String, Object>>() {}
            );

            if (response.getBody() != null && Boolean.TRUE.equals(response.getBody().get("success"))) {
                return mapToBatchSentimentResult(response.getBody());
            }
        } catch (Exception e) {
            log.error("批量NLP情感分析失败: {}", e.getMessage());
        }

        // 降级处理
        return BatchSentimentResult.builder()
            .averageScore(0.5)
            .positiveCount(0)
            .negativeCount(0)
            .neutralCount(texts.size())
            .build();
    }

    /**
     * 活动反馈综合分析
     */
    public ActivityFeedbackAnalysis analyzeActivityFeedback(Long activityId, List<Map<String, String>> feedbacks) {
        try {
            String url = aiServiceUrl + "/api/v3/ml/nlp/activity-feedback";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            Map<String, Object> request = new HashMap<>();
            request.put("activity_id", activityId.toString());
            request.put("feedbacks", feedbacks);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);

            var response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                new ParameterizedTypeReference<Map<String, Object>>() {}
            );

            if (response.getBody() != null && Boolean.TRUE.equals(response.getBody().get("success"))) {
                return mapToActivityFeedbackAnalysis(response.getBody());
            }
        } catch (Exception e) {
            log.error("活动反馈综合分析失败: {}", e.getMessage());
        }

        // 降级处理
        return ActivityFeedbackAnalysis.builder()
            .activityId(activityId)
            .totalFeedback(feedbacks.size())
            .averageSentiment(0.5)
            .build();
    }

    @SuppressWarnings("unchecked")
    private SentimentResult mapToSentimentResult(Map<String, Object> data) {
        return SentimentResult.builder()
            .text((String) data.get("text"))
            .sentimentScore(toDouble(data.get("sentiment_score")))
            .sentimentLevel((String) data.get("sentiment_level"))
            .confidence(toDouble(data.get("confidence")))
            .keywords((List<String>) data.get("keywords"))
            .aspectSentiments((Map<String, Double>) data.get("aspect_sentiments"))
            .build();
    }

    @SuppressWarnings("unchecked")
    private BatchSentimentResult mapToBatchSentimentResult(Map<String, Object> data) {
        return BatchSentimentResult.builder()
            .averageScore(toDouble(data.get("average_score")))
            .positiveCount(toInt(data.get("positive_count")))
            .negativeCount(toInt(data.get("negative_count")))
            .neutralCount(toInt(data.get("neutral_count")))
            .build();
    }

    @SuppressWarnings("unchecked")
    private ActivityFeedbackAnalysis mapToActivityFeedbackAnalysis(Map<String, Object> data) {
        return ActivityFeedbackAnalysis.builder()
            .activityId(Long.valueOf((String) data.get("activity_id")))
            .totalFeedback(toInt(data.get("total_feedback")))
            .averageSentiment(toDouble(data.get("average_sentiment")))
            .sentimentDistribution((Map<String, Integer>) data.get("sentiment_distribution"))
            .keyAspects((Map<String, Float>) data.get("key_aspects"))
            .suggestions((List<String>) data.get("suggestions"))
            .build();
    }

    private double toDouble(Object value) {
        if (value == null) return 0.0;
        if (value instanceof Number) return ((Number) value).doubleValue();
        try {
            return Double.parseDouble(value.toString());
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }

    private int toInt(Object value) {
        if (value == null) return 0;
        if (value instanceof Number) return ((Number) value).intValue();
        try {
            return Integer.parseInt(value.toString());
        } catch (NumberFormatException e) {
            return 0;
        }
    }
}
