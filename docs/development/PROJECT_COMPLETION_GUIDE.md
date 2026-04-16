# 校园社团活动系统 - 完善开发文档

**文档版本**: v1.0  
**更新日期**: 2026-04-15  
**目标**: 指导完成项目剩余功能开发

---

## 一、项目现状概览

### 1.1 整体完成度

| 模块 | 当前完成度 | 目标完成度 | 差距 |
|------|-----------|-----------|------|
| Java后端 | 70% | 95% | 25% |
| Python算法服务 | 75% | 90% | 15% |
| 社团端前端 | 65% | 90% | 25% |
| 管理端前端 | 50% | 85% | 35% |
| 学生端小程序 | 60% | 85% | 25% |

### 1.2 剩余开发工时估算

- **总工时**: 约 200 小时
- **推荐团队配置**: 2后端 + 2前端 + 1算法 = 5人
- **预计周期**: 4-5 周

---

## 二、开发阶段规划

### Phase 1: 基础设施完善 (Week 1)

#### 2.1.1 用户上下文工具类 (ISSUE-001)

**目标**: 解决硬编码用户ID问题

**文件**: `campus-main/src/main/java/com/campusclub/common/security/UserContext.java`

```java
package com.campusclub.common.security;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import com.campusclub.user.domain.entity.User;

public class UserContext {
    
    public static Long getCurrentUserId() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            throw new UnauthorizedException("用户未登录");
        }
        
        Object principal = auth.getPrincipal();
        if (principal instanceof User) {
            return ((User) principal).getId();
        }
        
        throw new IllegalStateException("无法获取当前用户ID");
    }
    
    public static Long getCurrentClubId() {
        Long userId = getCurrentUserId();
        // 通过ClubMemberRepository查询用户所属社团
        return ClubContextService.getClubIdByUserId(userId);
    }
    
    public static boolean hasRole(String role) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return auth.getAuthorities().stream()
            .anyMatch(a -> a.getAuthority().equals("ROLE_" + role));
    }
}
```

**修改清单**:
- [ ] 创建 `UserContext.java`
- [ ] 修改 `ResourceController.java` 所有硬编码 `1L`
- [ ] 修改 `EvaluationController.java` 所有硬编码
- [ ] 单元测试覆盖

---

#### 2.1.2 资金申请功能 (ISSUE-003)

**目标**: 实现活动经费申请流程

**数据库表**:

```sql
-- 资金申请表
CREATE TABLE fund_applications (
    id BIGSERIAL PRIMARY KEY,
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    activity_id BIGINT REFERENCES activities(id),
    applicant_id BIGINT NOT NULL REFERENCES users(id),
    amount DECIMAL(10, 2) NOT NULL,
    purpose TEXT NOT NULL,
    budget_breakdown JSONB,
    status VARCHAR(20) DEFAULT 'PENDING',
    reviewer_id BIGINT REFERENCES users(id),
    reviewer_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    version BIGINT DEFAULT 0
);

-- 索引
CREATE INDEX idx_fund_app_club ON fund_applications(club_id);
CREATE INDEX idx_fund_app_status ON fund_applications(status);
```

**实体类**: `campus-main/src/main/java/com/campusclub/fund/domain/entity/FundApplication.java`

```java
package com.campusclub.fund.domain.entity;

import com.campusclub.common.model.BaseEntity;
import jakarta.persistence.*;
import lombok.Data;
import lombok.EqualsAndHashCode;
import java.math.BigDecimal;

@Data
@Entity
@Table(name = "fund_applications")
@EqualsAndHashCode(callSuper = true)
public class FundApplication extends BaseEntity {
    
    public enum FundStatus {
        PENDING, APPROVED, REJECTED, CANCELLED
    }
    
    @ManyToOne
    @JoinColumn(name = "club_id", nullable = false)
    private Club club;
    
    @ManyToOne
    @JoinColumn(name = "activity_id")
    private Activity activity;
    
    @ManyToOne
    @JoinColumn(name = "applicant_id", nullable = false)
    private User applicant;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;
    
    @Column(nullable = false, length = 1000)
    private String purpose;
    
    @Column(columnDefinition = "jsonb")
    private String budgetBreakdown;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private FundStatus status = FundStatus.PENDING;
    
    @ManyToOne
    @JoinColumn(name = "reviewer_id")
    private User reviewer;
    
    private String reviewerComment;
}
```

**Controller**: `campus-main/src/main/java/com/campusclub/fund/controller/FundController.java`

```java
@RestController
@RequestMapping("/api/v1/funds")
@RequiredArgsConstructor
public class FundController {
    
    private final FundApplicationService fundService;
    
    @PostMapping("/applications")
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<FundApplicationDTO> apply(
            @Valid @RequestBody FundApplyRequest request) {
        Long clubId = UserContext.getCurrentClubId();
        FundApplicationDTO result = fundService.apply(request, clubId);
        return ApiResponse.success("申请提交成功", result);
    }
    
    @GetMapping("/applications/my")
    @PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
    public ApiResponse<Page<FundApplicationDTO>> getMyApplications(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Long clubId = UserContext.getCurrentClubId();
        return ApiResponse.success(fundService.getClubApplications(clubId, page, size));
    }
    
    @PostMapping("/applications/{id}/approve")
    @PreAuthorize("hasRole('ADMIN')")
    public ApiResponse<Void> approve(
            @PathVariable Long id,
            @RequestBody FundReviewRequest request) {
        Long adminId = UserContext.getCurrentUserId();
        fundService.review(id, FundStatus.APPROVED, request.getComment(), adminId);
        return ApiResponse.success("审批通过", null);
    }
}
```

---

### Phase 2: 核心功能完善 (Week 2-3)

#### 2.2.1 活动评价与NLP分析集成

**目标**: 学生提交评价后自动进行情感分析

**流程图**:
```
学生提交评价 → Java后端接收 → 发送MQ消息 → Python NLP服务消费 
                                        ↓
                                  情感分析计算
                                        ↓
                                  结果写回数据库 ← Java后端更新
```

**Java后端修改**:

```java
@Service
@RequiredArgsConstructor
public class ActivityFeedbackService {
    
    private final FeedbackRepository feedbackRepository;
    private final ApplicationEventPublisher eventPublisher;
    
    @Transactional
    public FeedbackDTO submitFeedback(FeedbackRequest request, Long userId) {
        // 保存评价
        Feedback feedback = new Feedback();
        feedback.setActivityId(request.getActivityId());
        feedback.setUserId(userId);
        feedback.setRating(request.getRating());
        feedback.setContent(request.getContent());
        feedback.setStatus(FeedbackStatus.PENDING_ANALYSIS);
        
        feedbackRepository.save(feedback);
        
        // 发布事件，异步触发NLP分析
        eventPublisher.publishEvent(new FeedbackSubmittedEvent(feedback));
        
        return FeedbackMapper.toDTO(feedback);
    }
}

@Component
@RequiredArgsConstructor
public class FeedbackEventListener {
    
    private final AlgorithmService algorithmService;
    private final FeedbackRepository feedbackRepository;
    
    @Async
    @EventListener
    public void handleFeedbackSubmitted(FeedbackSubmittedEvent event) {
        Feedback feedback = event.getFeedback();
        
        try {
            // 调用Python NLP服务
            NLPAnalysisResult result = algorithmService.analyzeSentiment(feedback.getContent());
            
            // 更新分析结果
            feedback.setSentimentScore(result.getSentimentScore());
            feedback.setSentimentLevel(result.getSentimentLevel());
            feedback.setKeywords(result.getKeywords());
            feedback.setStatus(FeedbackStatus.ANALYZED);
            
            feedbackRepository.save(feedback);
        } catch (Exception e) {
            log.error("NLP分析失败", e);
            feedback.setStatus(FeedbackStatus.ANALYSIS_FAILED);
            feedbackRepository.save(feedback);
        }
    }
}
```

**Python NLP API扩展**:

```python
# campus-ai/src/api/v3/nlp.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from ...core.nlp_analyzer import NLPSentimentAnalyzer

router = APIRouter(prefix="/nlp", tags=["v3-nlp"])

analyzer = NLPSentimentAnalyzer()

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    sentiment_score: float
    sentiment_level: str
    keywords: List[str]
    aspect_sentiments: dict

@router.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    result = analyzer.analyze(request.text)
    return SentimentResponse(
        sentiment_score=result.sentiment_score,
        sentiment_level=result.sentiment_level,
        keywords=result.keywords,
        aspect_sentiments=result.aspect_sentiments
    )
```

---

#### 2.2.2 学生端推荐算法接入

**目标**: 首页展示个性化活动推荐

**Java API**:

```java
@RestController
@RequestMapping("/api/v1/recommendations")
@RequiredArgsConstructor
public class RecommendationController {
    
    private final AlgorithmService algorithmService;
    private final ActivityRepository activityRepository;
    
    @GetMapping("/activities")
    @SecurityRequirement(name = "bearerAuth")
    public ApiResponse<List<ActivityDTO>> getRecommendedActivities(
            @AuthenticationPrincipal Long userId) {
        
        // 获取用户历史行为
        List<UserActivityHistory> history = getUserHistory(userId);
        
        // 调用Python聚类算法
        RecommendationRequest request = new RecommendationRequest();
        request.setUserId(userId);
        request.setHistory(convertToAlgorithmFormat(history));
        
        RecommendationResult result = algorithmService.getRecommendations(request);
        
        // 根据推荐的活动ID获取详情
        List<Activity> activities = activityRepository
            .findAllById(result.getRecommendedActivityIds());
        
        return ApiResponse.success(
            activities.stream()
                .map(ActivityMapper::toDTO)
                .collect(Collectors.toList())
        );
    }
}
```

**学生端页面修改**:

```vue
<!-- campus-frontend/packages/student/src/pages/index/index.vue -->

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { recommendationApi } from '@/api/recommendation';

const recommendedActivities = ref<Activity[]>([]);

async function loadRecommendations() {
  try {
    const response = await recommendationApi.getRecommendations();
    recommendedActivities.value = response.data;
  } catch (error) {
    console.error('获取推荐失败', error);
    // 降级：显示热门活动
    loadHotActivities();
  }
}

onMounted(() => {
  loadRecommendations();
});
</script>
```

---

### Phase 3: 管理端功能完善 (Week 3-4)

#### 2.3.1 全局数据监控大屏

**目标**: 为管理员提供全校社团活动数据可视化

**后端聚合API**:

```java
@RestController
@RequestMapping("/api/v1/dashboard")
@PreAuthorize("hasRole('ADMIN')")
@RequiredArgsConstructor
public class DashboardController {
    
    private final DashboardService dashboardService;
    
    @GetMapping("/overview")
    public ApiResponse<DashboardOverviewDTO> getOverview() {
        return ApiResponse.success(dashboardService.getOverview());
    }
    
    @GetMapping("/activity-trends")
    public ApiResponse<List<TrendDataDTO>> getActivityTrends(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate end) {
        return ApiResponse.success(dashboardService.getActivityTrends(start, end));
    }
    
    @GetMapping("/club-rankings")
    public ApiResponse<List<ClubRankingDTO>> getClubRankings(
            @RequestParam(defaultValue = "ACTIVITY_COUNT") RankingType type) {
        return ApiResponse.success(dashboardService.getClubRankings(type));
    }
    
    @GetMapping("/resource-usage")
    public ApiResponse<ResourceUsageDTO> getResourceUsage() {
        return ApiResponse.success(dashboardService.getResourceUsage());
    }
}
```

**DashboardService实现**:

```java
@Service
@RequiredArgsConstructor
public class DashboardService {
    
    private final ActivityRepository activityRepository;
    private final ClubRepository clubRepository;
    private final ResourceBookingRepository bookingRepository;
    
    public DashboardOverviewDTO getOverview() {
        DashboardOverviewDTO dto = new DashboardOverviewDTO();
        
        // 统计数据
        dto.setTotalActivities(activityRepository.count());
        dto.setActiveClubs(clubRepository.countActive());
        dto.setTotalParticipants(activityRepository.countTotalParticipants());
        dto.setPendingApprovals(activityRepository.countByStatus(ActivityStatus.PENDING_APPROVAL));
        
        // 本周活动趋势
        dto.setWeeklyNewActivities(activityRepository.countThisWeek());
        dto.setWeeklyGrowthRate(calculateGrowthRate());
        
        // 满意度统计
        dto.setAverageRating(activityRepository.getAverageRating());
        dto.setTotalReviews(activityRepository.countReviews());
        
        return dto;
    }
}
```

**管理端大屏页面**:

```vue
<!-- campus-frontend/packages/admin/src/views/dashboard/index.vue -->

<template>
  <div class="dashboard-page">
    <!-- 概览卡片 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in overviewCards" :key="card.title">
        <overview-card :data="card" />
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <activity-trend-chart :data="trendData" />
      </el-col>
      <el-col :span="12">
        <club-ranking-chart :data="rankingData" />
      </el-col>
    </el-row>
    
    <!-- 实时数据 -->
    <el-row :gutter="20" class="realtime-row">
      <el-col :span="16">
        <recent-activities-table />
      </el-col>
      <el-col :span="8">
        <resource-usage-chart />
      </el-col>
    </el-row>
  </div>
</template>
```

---

#### 2.3.2 智能审批系统集成

**目标**: 结合LSTM预测辅助管理员审批资源申请

**审批流程**:

```java
@Service
@RequiredArgsConstructor
public class SmartApprovalService {
    
    private final AlgorithmService algorithmService;
    private final ActivityRepository activityRepository;
    
    public ApprovalSuggestion getSuggestion(Long activityId) {
        Activity activity = activityRepository.findById(activityId)
            .orElseThrow(() -> new NotFoundException("活动不存在"));
        
        // 1. LSTM预测资源需求
        ResourceForecast forecast = algorithmService.forecastResourceDemand(
            activity.getType(),
            activity.getPlannedDate()
        );
        
        // 2. GA优化资源分配
        ResourceAllocation allocation = algorithmService.optimizeAllocation(
            activity,
            forecast
        );
        
        // 3. 生成审批建议
        ApprovalSuggestion suggestion = new ApprovalSuggestion();
        suggestion.setSuccessProbability(calculateSuccessProbability(activity));
        suggestion.setRecommendedVenue(allocation.getRecommendedVenue());
        suggestion.setResourceConflicts(allocation.getConflicts());
        suggestion.setAiRecommendation(generateRecommendation(activity, allocation));
        
        return suggestion;
    }
}
```

---

### Phase 4: 算法服务完善 (Week 4-5)

#### 2.4.1 CV图像分析实现

**目标**: 分析学生上传的活动照片质量

```python
# campus-ai/src/core/image_analyzer.py

import cv2
import numpy as np
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ImageAnalysisResult:
    quality_score: float
    crowd_density: float
    clarity_score: float
    brightness_score: float
    suggestions: List[str]

class ActivityImageAnalyzer:
    """
    活动照片质量分析器
    
    分析维度：
    1. 清晰度（锐度检测）
    2. 人群密度（人脸识别计数）
    3. 光线充足度
    4. 构图质量
    """
    
    def __init__(self):
        # 加载人脸检测模型
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def analyze(self, image_path: str) -> ImageAnalysisResult:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 1. 清晰度分析
        clarity = self._analyze_clarity(image)
        
        # 2. 人群密度分析
        crowd_density = self._analyze_crowd(image)
        
        # 3. 光线分析
        brightness = self._analyze_brightness(image)
        
        # 4. 综合评分
        quality_score = self._calculate_quality_score(
            clarity, crowd_density, brightness
        )
        
        # 5. 生成建议
        suggestions = self._generate_suggestions(
            clarity, crowd_density, brightness
        )
        
        return ImageAnalysisResult(
            quality_score=quality_score,
            crowd_density=crowd_density,
            clarity_score=clarity,
            brightness_score=brightness,
            suggestions=suggestions
        )
    
    def _analyze_clarity(self, image: np.ndarray) -> float:
        """使用拉普拉斯算子检测清晰度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        # 归一化到0-1
        return min(1.0, laplacian_var / 500)
    
    def _analyze_crowd(self, image: np.ndarray) -> float:
        """检测人群密度"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # 根据图片尺寸和检测到的人脸数计算密度
        image_area = image.shape[0] * image.shape[1]
        face_area = sum(w * h for (_, _, w, h) in faces)
        density = face_area / image_area
        
        return min(1.0, density * 10)  # 归一化
    
    def _analyze_brightness(self, image: np.ndarray) -> float:
        """分析光线充足度"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        brightness = np.mean(hsv[:, :, 2])
        return brightness / 255.0
    
    def _calculate_quality_score(self, clarity: float, 
                                  crowd: float, 
                                  brightness: float) -> float:
        """综合质量评分"""
        weights = {'clarity': 0.4, 'crowd': 0.3, 'brightness': 0.3}
        score = (clarity * weights['clarity'] +
                 crowd * weights['crowd'] +
                 brightness * weights['brightness'])
        return round(score, 2)
    
    def _generate_suggestions(self, clarity: float,
                              crowd: float,
                              brightness: float) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if clarity < 0.5:
            suggestions.append("照片清晰度较低，建议重新上传更清晰的图片")
        
        if crowd < 0.2:
            suggestions.append("照片中参与人数较少，建议上传更多人参与的照片")
        
        if brightness < 0.3:
            suggestions.append("照片光线较暗，建议在光线充足的环境下拍摄")
        elif brightness > 0.9:
            suggestions.append("照片光线过强，建议调整曝光")
        
        return suggestions
```

---

## 三、API接口汇总

### 3.1 新增接口清单

| 模块 | 接口 | 方法 | 描述 |
|------|------|------|------|
| 资金 | /api/v1/funds/applications | POST | 提交资金申请 |
| 资金 | /api/v1/funds/applications/my | GET | 查询我的申请 |
| 资金 | /api/v1/funds/applications/{id}/approve | POST | 审批资金申请 |
| 评价 | /api/v1/activities/{id}/feedback | POST | 提交活动评价 |
| 评价 | /api/v1/activities/{id}/feedback/analysis | GET | 获取评价分析 |
| 推荐 | /api/v1/recommendations/activities | GET | 获取推荐活动 |
| 大屏 | /api/v1/dashboard/overview | GET | 数据概览 |
| 大屏 | /api/v1/dashboard/activity-trends | GET | 活动趋势 |
| 审批 | /api/v1/approvals/{id}/suggestion | GET | 获取审批建议 |
| 图片 | /api/v1/activities/{id}/photos/analyze | POST | 分析活动照片 |

---

## 四、测试策略

### 4.1 单元测试要求

每个新增功能必须包含：
- Controller层: WebMvcTest
- Service层: Mockito单元测试
- Repository层: DataJpaTest

### 4.2 集成测试

```java
@SpringBootTest
@AutoConfigureMockMvc
public class FundApplicationIntegrationTest {
    
    @Test
    void shouldCompleteFundApplicationWorkflow() {
        // 1. 提交申请
        // 2. 查询申请
        // 3. 管理员审批
        // 4. 验证状态
    }
}
```

---

## 五、部署检查清单

### 5.1 生产环境配置

- [ ] PostgreSQL连接池配置优化
- [ ] Redis缓存开启
- [ ] Python算法服务健康检查
- [ ] 日志级别调整为INFO
- [ ] 启用Flyway数据库迁移

### 5.2 监控告警

- [ ] 接口响应时间监控 (P95 < 2s)
- [ ] 错误率监控 (< 0.1%)
- [ ] 算法服务可用性监控
- [ ] 数据库连接池监控

---

**文档维护**: 每周更新进度  
**问题反馈**: 在本文档添加注释或创建Issue
