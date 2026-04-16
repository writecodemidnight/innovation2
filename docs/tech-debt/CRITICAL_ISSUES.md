# 技术债务与紧急修复报告

**文档版本**: v1.0  
**生成日期**: 2026-04-15  
**文档级别**: 🔴 内部机密 - 开发团队专用

---

## 执行摘要

本报告通过代码扫描识别出 **3个红色警报级问题** 和 **5个黄色预警级问题**。红色警报问题必须在 **下周代码冻结前** 修复，否则将影响权限系统（RBAC）的接入，导致大规模重构。

| 级别 | 数量 | 预计修复工时 |
|------|------|--------------|
| 🔴 红色警报 | 3 | 16小时 |
| 🟡 黄色预警 | 5 | 24小时 |
| 🟢 技术债务 | 8 | 40小时 |

---

## 🔴 红色警报：必须立即修复的"暗雷"

### ISSUE-001: 用户上下文硬编码 (1L 问题)

**风险等级**: 🔴 CRITICAL  
**影响范围**: ResourceController, EvaluationController  
**预计修复**: 4小时

#### 问题描述

在以下位置发现硬编码的用户ID (`1L`)：

```java
// campus-main/src/main/java/com/campusclub/resource/controller/ResourceController.java:67
Long clubId = 1L; // 临时使用

// campus-main/src/main/java/com/campusclub/resource/controller/ResourceController.java:84
Long applicantId = 1L; // 临时使用

// campus-main/src/main/java/com/campusclub/resource/controller/ResourceController.java:100
Long applicantId = 1L; // 临时使用
```

#### 为什么这是"暗雷"

1. **权限绕过**: 所有资源操作都变成了用户1的操作，无法区分真实用户
2. **数据污染**: 测试数据和真实数据混杂
3. **RBAC阻断**: 接入Spring Security后，这些代码将全部失效

#### 修复方案

**步骤1**: 创建 UserContext 工具类

```java
package com.campusclub.common.security;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;

public class UserContext {
    
    public static Long getCurrentUserId() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            throw new UnauthorizedException("用户未登录");
        }
        
        Object principal = auth.getPrincipal();
        if (principal instanceof UserDetails) {
            // 从UserDetails中提取用户ID
            return extractUserId((UserDetails) principal);
        }
        
        throw new IllegalStateException("无法获取当前用户ID");
    }
    
    public static Long getCurrentClubId() {
        // 根据用户角色获取所属社团ID
        Long userId = getCurrentUserId();
        return ClubService.getClubIdByUserId(userId);
    }
    
    public static boolean isAdmin() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return auth.getAuthorities().stream()
            .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
    }
}
```

**步骤2**: 修改 ResourceController

```java
@PostMapping("/bookings")
@PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
public ApiResponse<ResourceBookingDTO> createBooking(
        @Valid @RequestBody BookingRequestDTO request) {
    Long clubId = UserContext.getCurrentClubId();
    ResourceBookingDTO booking = resourceService.createBooking(request, clubId);
    return ApiResponse.success("预约申请提交成功", booking);
}
```

---

### ISSUE-002: 算法服务熔断降级缺失

**风险等级**: 🔴 CRITICAL  
**影响范围**: AlgorithmService  
**预计修复**: 6小时

#### 问题描述

当前算法服务调用失败时直接抛出异常，没有降级方案：

```java
// AlgorithmService.java:101
private AlgorithmResponse executeAlgorithm(AlgorithmRequest request) {
    String url = algorithmServiceUrl + "/api/v1/algorithms/" + request.getAlgorithmType().toLowerCase();
    return restTemplate.postForObject(url, request, AlgorithmResponse.class); // 可能NPE
}
```

#### 修复方案

实现熔断降级模式：

```java
@Service
@Slf4j
public class AlgorithmService {
    
    private final CircuitBreaker circuitBreaker = CircuitBreaker.ofDefaults("algorithm");
    
    public AlgorithmResponse executeWithFallback(AlgorithmRequest request) {
        return circuitBreaker.executeSupplier(() -> {
            try {
                return executeAlgorithm(request);
            } catch (Exception e) {
                log.warn("算法服务调用失败，使用降级方案", e);
                return getFallbackResponse(request);
            }
        });
    }
    
    private AlgorithmResponse getFallbackResponse(AlgorithmRequest request) {
        return switch (request.getAlgorithmType().toUpperCase()) {
            case "AHP" -> getDefaultAHPResponse();
            case "KMEANS" -> getDefaultKMeansResponse();
            case "LSTM" -> getDefaultLSTMResponse();
            default -> throw new AlgorithmException("无可用降级方案");
        };
    }
    
    private AlgorithmResponse getDefaultAHPResponse() {
        // 返回预设的权重配置
        Map<String, Object> defaultWeights = Map.of(
            "参与度", 0.32,
            "教育性", 0.18,
            "创新性", 0.15,
            "影响力", 0.22,
            "可持续性", 0.13
        );
        return new AlgorithmResponse(true, "使用默认权重", defaultWeights);
    }
}
```

---

### ISSUE-003: 资金申请功能完全缺失

**风险等级**: 🔴 CRITICAL  
**影响范围**: 社团端核心业务流程  
**预计修复**: 6小时

#### 问题描述

设计文档中要求支持"申请场地、设备、资金"，但目前只有场地和设备的预约，**资金申请功能完全缺失**。

#### 影响

- 社团无法申请活动经费
- 资源优化配置系统不完整

#### 修复方案

**数据库实体**:

```java
@Entity
@Table(name = "fund_applications")
public class FundApplication {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "club_id")
    private Club club;
    
    @ManyToOne
    @JoinColumn(name = "activity_id")
    private Activity activity;
    
    private BigDecimal amount;
    private String purpose;
    private String budgetBreakdown;
    
    @Enumerated(EnumType.STRING)
    private FundStatus status; // PENDING, APPROVED, REJECTED
    
    private LocalDateTime createdAt;
    private LocalDateTime reviewedAt;
    private String reviewerComment;
}
```

---

## 🟡 黄色预警：需要关注的设计缺陷

### ISSUE-004: 活动评价与NLP分析脱节

**问题**: 学生提交的评价没有触发NLP情感分析  
**建议**: 在评价提交后异步调用Python NLP服务

```java
@EventListener
public void onFeedbackSubmitted(FeedbackSubmittedEvent event) {
    // 异步调用NLP分析
    nlpAnalysisService.analyzeAsync(event.getFeedbackId());
}
```

### ISSUE-005: Redis缓存配置生产环境缺失

**问题**: `application-local.yml` 中禁用了Redis  
**风险**: 生产环境需要Redis做分布式锁和缓存

### ISSUE-006: 遗传算法调度任务缺乏监控

**问题**: GA调度任务执行时间可能长达5-10分钟，但没有进度查询接口  
**建议**: 添加任务状态查询和WebSocket进度推送

### ISSUE-007: 图片上传缺少CV分析

**问题**: 设计文档要求CV分析照片质量，目前仅实现上传存储  
**建议**: 接入 `campus-ai/src/core/image_analyzer.py`

### ISSUE-008: 学生端推荐算法未接入

**问题**: K-Means聚类算法已实现，但学生端首页未调用  
**建议**: 添加推荐API调用

---

## 🟢 技术债务：需要长期改进

| 编号 | 问题 | 优先级 | 建议方案 |
|------|------|--------|----------|
| DEBT-001 | 单元测试覆盖率低于30% | 中 | 为核心Service添加测试 |
| DEBT-002 | API版本管理混乱 (v1/v3混用) | 低 | 统一使用v1，废弃v3 |
| DEBT-003 | 数据库缺少索引优化 | 中 | 为高频查询字段加索引 |
| DEBT-004 | 日志格式不统一 | 低 | 使用结构化日志 |
| DEBT-005 | 缺少API限流 | 高 | 添加RateLimiter |
| DEBT-006 | 异常处理不一致 | 中 | 统一GlobalExceptionHandler |
| DEBT-007 | 前端类型定义分散 | 低 | 统一使用shared包 |
| DEBT-008 | 缺少数据库迁移脚本 | 高 | 启用Flyway |

---

## 修复路线图

### 第一阶段：红色警报 (本周完成)

- [ ] Day 1-2: 实现 UserContext 工具类，修复1L硬编码
- [ ] Day 3: 实现 AlgorithmService 熔断降级
- [ ] Day 4-5: 实现资金申请功能

### 第二阶段：黄色预警 (下周完成)

- [ ] 接入NLP情感分析
- [ ] 配置生产环境Redis
- [ ] 添加GA任务监控接口

### 第三阶段：技术债务 (后续迭代)

- [ ] 提升测试覆盖率
- [ ] 添加API限流
- [ ] 启用Flyway

---

## 附录：快速修复检查清单

```markdown
## 每日站会检查项

- [ ] 今天是否检查了新的硬编码ID？
- [ ] 所有Controller是否使用UserContext？
- [ ] 新接口是否有熔断降级方案？
- [ ] 数据库变更是否有Flyway脚本？
```

---

**报告生成**: Claude Code + 自动化代码扫描  
**下次审查**: 2026-04-22
