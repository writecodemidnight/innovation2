package com.campusclub.recommendation.service;

import com.campusclub.activity.application.dto.ActivityDto;
import com.campusclub.activity.domain.entity.Activity;
import com.campusclub.activity.domain.repository.ActivityRepository;
import com.campusclub.activity.application.mapper.ActivityMapper;
import com.campusclub.club.domain.entity.Club;
import com.campusclub.club.domain.repository.ClubRepository;
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

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class RecommendationService {

    private final ActivityRepository activityRepository;
    private final ClubRepository clubRepository;
    private final ActivityMapper activityMapper;
    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${ai.service.url:http://localhost:8000}")
    private String aiServiceUrl;

    /**
     * 基于K-Means聚类的个性化活动推荐
     */
    public List<ActivityDto> getPersonalizedRecommendations(Long userId) {
        try {
            // 1. 获取所有活动
            List<Activity> allActivities = activityRepository.findAll();

            // 2. 准备学生特征数据
            List<Map<String, Object>> studentFeatures = prepareStudentFeatures(userId);

            // 3. 调用K-Means聚类API
            Map<String, Object> clusteringRequest = new HashMap<>();
            clusteringRequest.put("data", studentFeatures);
            clusteringRequest.put("k", 5);

            Map<String, Object> clusteringResult = callKMeansClustering(clusteringRequest);

            // 4. 根据聚类结果筛选相似活动
            List<Long> recommendedActivityIds = filterActivitiesByClusterResult(
                allActivities, clusteringResult, userId
            );

            // 5. 获取推荐活动详情
            List<Activity> recommendedActivities = activityRepository.findAllById(recommendedActivityIds);

            // 6. 按热度排序并限制数量
            return enrichWithClubName(recommendedActivities.stream()
                .filter(a -> !isActivityExpired(a))
                .sorted(Comparator.comparing(Activity::getCurrentParticipants).reversed())
                .limit(10)
                .toList());

        } catch (Exception e) {
            log.error("个性化推荐失败: {}", e.getMessage(), e);
            // 降级到默认推荐
            return getDefaultRecommendations();
        }
    }

    /**
     * 获取热门推荐（默认推荐）
     */
    public List<ActivityDto> getDefaultRecommendations() {
        List<Activity> hotActivities = activityRepository.findHotActivities(
            org.springframework.data.domain.Pageable.ofSize(10)
        );
        return enrichWithClubName(hotActivities);
    }

    /**
     * 准备学生特征数据用于聚类
     */
    private List<Map<String, Object>> prepareStudentFeatures(Long userId) {
        List<Map<String, Object>> features = new ArrayList<>();

        // 当前学生的特征（简化版）
        Map<String, Object> currentStudent = new HashMap<>();
        currentStudent.put("student_id", userId.toString());
        currentStudent.put("academic_score", 0.7); // 学业成绩
        currentStudent.put("social_score", 0.5);   // 社交活跃度
        currentStudent.put("art_score", 0.3);      // 艺术偏好
        currentStudent.put("sports_score", 0.4);   // 体育偏好
        currentStudent.put("tech_score", 0.8);     // 科技偏好
        features.add(currentStudent);

        // 添加一些模拟的其他学生数据用于聚类
        for (int i = 1; i <= 20; i++) {
            Map<String, Object> mockStudent = new HashMap<>();
            mockStudent.put("student_id", "mock_" + i);
            mockStudent.put("academic_score", Math.random());
            mockStudent.put("social_score", Math.random());
            mockStudent.put("art_score", Math.random());
            mockStudent.put("sports_score", Math.random());
            mockStudent.put("tech_score", Math.random());
            features.add(mockStudent);
        }

        return features;
    }

    /**
     * 调用K-Means聚类API
     */
    private Map<String, Object> callKMeansClustering(Map<String, Object> request) {
        String url = aiServiceUrl + "/api/v1/algorithms/kmeans";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, Object> algorithmRequest = new HashMap<>();
        algorithmRequest.put("algorithmType", "KMEANS");
        algorithmRequest.put("parameters", request);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(algorithmRequest, headers);

        try {
            var response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                new ParameterizedTypeReference<Map<String, Object>>() {}
            );

            if (response.getBody() != null && Boolean.TRUE.equals(response.getBody().get("success"))) {
                @SuppressWarnings("unchecked")
                Map<String, Object> result = (Map<String, Object>) response.getBody().get("result");
                return result != null ? result : new HashMap<>();
            }
        } catch (Exception e) {
            log.error("调用K-Means算法失败: {}", e.getMessage());
        }

        return new HashMap<>();
    }

    /**
     * 根据聚类结果筛选活动
     */
    private List<Long> filterActivitiesByClusterResult(
            List<Activity> activities,
            Map<String, Object> clusteringResult,
            Long userId) {

        @SuppressWarnings("unchecked")
        List<Integer> clusters = (List<Integer>) clusteringResult.get("clusters");

        if (clusters == null || clusters.isEmpty()) {
            // 返回最热门的活动
            return activities.stream()
                .sorted(Comparator.comparing(Activity::getCurrentParticipants).reversed())
                .limit(10)
                .map(Activity::getId)
                .toList();
        }

        // 获取当前用户的聚类标签
        int userCluster = clusters.get(0);

        // 根据聚类标签推荐不同类型的活动
        Activity.ActivityType preferredType = mapClusterToActivityType(userCluster);

        return activities.stream()
            .filter(a -> preferredType == null || a.getActivityType() == preferredType)
            .filter(a -> a.getStatus() == Activity.ActivityStatus.REGISTERING ||
                        a.getStatus() == Activity.ActivityStatus.APPROVED)
            .map(Activity::getId)
            .toList();
    }

    /**
     * 将聚类标签映射到活动类型
     */
    private Activity.ActivityType mapClusterToActivityType(int cluster) {
        return switch (cluster) {
            case 0 -> Activity.ActivityType.LECTURE;      // 学术型 - 讲座
            case 1 -> Activity.ActivityType.SPORTS;       // 体育型
            case 2 -> Activity.ActivityType.ENTERTAINMENT; // 艺术型 - 娱乐
            case 3 -> Activity.ActivityType.SOCIAL;       // 社交型
            case 4 -> Activity.ActivityType.VOLUNTEER;    // 志愿型
            default -> null;
        };
    }

    private boolean isActivityExpired(Activity activity) {
        return activity.getEndTime() != null &&
               activity.getEndTime().isBefore(LocalDateTime.now());
    }

    private List<ActivityDto> enrichWithClubName(List<Activity> activities) {
        Map<Long, String> clubNameMap = getClubNameMap(
            activities.stream()
                .map(Activity::getClubId)
                .filter(id -> id != null)
                .toList()
        );

        return activities.stream()
            .map(activity -> {
                ActivityDto dto = activityMapper.toDto(activity);
                return copyWithClubName(dto, clubNameMap.getOrDefault(dto.clubId(), null));
            })
            .toList();
    }

    private Map<Long, String> getClubNameMap(List<Long> clubIds) {
        if (clubIds.isEmpty()) {
            return Map.of();
        }
        return clubRepository.findAllById(clubIds).stream()
            .collect(Collectors.toMap(Club::getId, Club::getName));
    }

    private ActivityDto copyWithClubName(ActivityDto dto, String clubName) {
        return new ActivityDto(
            dto.id(),
            dto.title(),
            dto.description(),
            dto.activityType(),
            dto.status(),
            dto.startTime(),
            dto.endTime(),
            dto.location(),
            dto.capacity(),
            dto.currentParticipants(),
            dto.clubId(),
            clubName,
            dto.createdBy(),
            dto.coverImageUrl(),
            dto.budget(),
            dto.approvalStatus(),
            dto.registrationDeadline(),
            dto.createdAt()
        );
    }
}
