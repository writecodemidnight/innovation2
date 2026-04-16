# Java 后端开发指南

本文档介绍 Java 后端模块的开发规范和最佳实践。

---

## 目录

1. [项目结构](#项目结构)
2. [开发规范](#开发规范)
3. [核心功能实现](#核心功能实现)
4. [常见问题](#常见问题)

---

## 项目结构

```
campus-main/src/main/java/com/campusclub/
├── common/                      # 公共模块
│   ├── config/                  # 配置类
│   ├── exception/               # 异常定义
│   ├── security/                # 安全相关
│   │   ├── UserContext.java     # 用户上下文
│   │   └── JwtTokenProvider.java
│   └── util/                    # 工具类
│
├── user/                        # 用户模块
│   ├── controller/              # 控制器
│   ├── service/                 # 服务层
│   │   ├── UserService.java
│   │   └── impl/
│   ├── repository/              # 数据访问
│   └── domain/
│       ├── entity/              # 实体类
│       └── dto/                 # 数据传输对象
│
├── club/                        # 社团模块
├── activity/                    # 活动模块
├── resource/                    # 资源模块
├── evaluation/                  # 评估模块
└── fund/                        # 资金模块
```

---

## 开发规范

### 包命名规范

```
com.campusclub.{module}.{layer}
```

| 层 | 命名 | 示例 |
|----|------|------|
| 控制器 | controller | `com.campusclub.user.controller` |
| 服务 | service | `com.campusclub.user.service` |
| 数据访问 | repository | `com.campusclub.user.repository` |
| 实体 | domain.entity | `com.campusclub.user.domain.entity` |
| DTO | domain.dto | `com.campusclub.user.domain.dto` |

### 类命名规范

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| 实体类 | 名词 | `User`, `Club`, `Activity` |
| 控制器 | 名词 + Controller | `UserController` |
| 服务接口 | 名词 + Service | `UserService` |
| 服务实现 | 名词 + ServiceImpl | `UserServiceImpl` |
| 仓库 | 名词 + Repository | `UserRepository` |
| DTO | 名词 + DTO/Request/Response | `UserDTO`, `LoginRequest` |
| 异常 | 名词 + Exception | `BusinessException` |

### 代码风格

#### Controller 层

```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Tag(name = "用户管理", description = "用户相关接口")
public class UserController {

    private final UserService userService;

    @GetMapping("/me")
    @Operation(summary = "获取当前用户信息")
    @SecurityRequirement(name = "bearerAuth")
    public ApiResponse<UserDTO> getCurrentUser(
            @AuthenticationPrincipal UserDetails userDetails) {
        UserDTO user = userService.getUserByUsername(userDetails.getUsername());
        return ApiResponse.success(user);
    }

    @PostMapping
    @Operation(summary = "创建用户")
    @PreAuthorize("hasRole('ADMIN')")
    public ApiResponse<UserDTO> createUser(
            @Valid @RequestBody UserCreateRequest request) {
        UserDTO user = userService.createUser(request);
        return ApiResponse.success("创建成功", user);
    }
}
```

#### Service 层

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;
    private final UserMapper userMapper;

    @Override
    @Transactional(readOnly = true)
    public UserDTO getUserById(Long id) {
        return userRepository.findById(id)
                .map(userMapper::toDTO)
                .orElseThrow(() -> new NotFoundException("用户不存在: " + id));
    }

    @Override
    @Transactional
    public UserDTO createUser(UserCreateRequest request) {
        // 检查用户名唯一性
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new BusinessException("用户名已存在");
        }

        User user = userMapper.toEntity(request);
        user.setPassword(passwordEncoder.encode(request.getPassword()));

        User saved = userRepository.save(user);
        log.info("创建用户成功: {}", saved.getUsername());

        return userMapper.toDTO(saved);
    }
}
```

---

## 核心功能实现

### 1. UserContext 用户上下文

**文件**: `common/security/UserContext.java`

```java
package com.campusclub.common.security;

import com.campusclub.user.domain.entity.User;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

@Component
public class UserContext {

    /**
     * 获取当前登录用户ID
     */
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

    /**
     * 获取当前用户所属社团ID
     */
    public static Long getCurrentClubId() {
        Long userId = getCurrentUserId();
        // 通过用户角色获取所属社团
        // 实际实现需要根据业务逻辑调整
        return ClubService.getClubIdByUserId(userId);
    }

    /**
     * 检查当前用户是否有指定角色
     */
    public static boolean hasRole(String role) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null) return false;

        return auth.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_" + role));
    }
}
```

**使用示例**:

```java
@PostMapping("/bookings")
@PreAuthorize("hasAnyRole('CLUB_PRESIDENT', 'CLUB_MANAGER')")
public ApiResponse<ResourceBookingDTO> createBooking(
        @Valid @RequestBody BookingRequestDTO request) {
    // 使用 UserContext 获取当前用户clubId，替代硬编码 1L
    Long clubId = UserContext.getCurrentClubId();
    ResourceBookingDTO booking = resourceService.createBooking(request, clubId);
    return ApiResponse.success("预约申请提交成功", booking);
}
```

### 2. 统一异常处理

**文件**: `common/exception/GlobalExceptionHandler.java`

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ApiResponse<Void> handleBusinessException(BusinessException e) {
        log.warn("业务异常: {}", e.getMessage());
        return ApiResponse.error(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(NotFoundException.class)
    public ApiResponse<Void> handleNotFoundException(NotFoundException e) {
        log.warn("资源不存在: {}", e.getMessage());
        return ApiResponse.error("NOT_FOUND", e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ApiResponse<Void> handleValidationException(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .collect(Collectors.joining(", "));
        return ApiResponse.error("VALIDATION_ERROR", message);
    }

    @ExceptionHandler(Exception.class)
    public ApiResponse<Void> handleException(Exception e) {
        log.error("系统异常", e);
        return ApiResponse.error("INTERNAL_ERROR", "系统繁忙，请稍后重试");
    }
}
```

### 3. 算法服务熔断降级

**文件**: `evaluation/service/AlgorithmService.java`

```java
@Service
@Slf4j
@RequiredArgsConstructor
public class AlgorithmService {

    private final RestTemplate restTemplate;
    private final CircuitBreakerRegistry circuitBreakerRegistry;

    @Value("${algorithm.service.url}")
    private String algorithmServiceUrl;

    /**
     * 调用算法服务（带熔断降级）
     */
    public AlgorithmResponse executeWithFallback(AlgorithmRequest request) {
        CircuitBreaker circuitBreaker = circuitBreakerRegistry.circuitBreaker("algorithm");

        return circuitBreaker.executeSupplier(() -> {
            try {
                return executeAlgorithm(request);
            } catch (Exception e) {
                log.warn("算法服务调用失败，使用降级方案", e);
                return getFallbackResponse(request);
            }
        });
    }

    private AlgorithmResponse executeAlgorithm(AlgorithmRequest request) {
        String url = algorithmServiceUrl + "/api/v3/" + request.getAlgorithmType().toLowerCase();
        return restTemplate.postForObject(url, request, AlgorithmResponse.class);
    }

    private AlgorithmResponse getFallbackResponse(AlgorithmRequest request) {
        return switch (request.getAlgorithmType().toUpperCase()) {
            case "EVALUATION" -> getDefaultEvaluationResponse();
            case "CLUSTERING" -> getDefaultClusteringResponse();
            default -> throw new AlgorithmException("无可用降级方案: " + request.getAlgorithmType());
        };
    }

    private AlgorithmResponse getDefaultEvaluationResponse() {
        Map<String, Object> defaultResult = Map.of(
            "weights", Map.of(
                "参与度", 0.32,
                "教育性", 0.18,
                "创新性", 0.15,
                "影响力", 0.22,
                "可持续性", 0.13
            ),
            "consistency_ratio", 0.03,
            "consistency_check_passed", true
        );
        return new AlgorithmResponse(true, "使用默认配置", defaultResult);
    }
}
```

### 4. 事件驱动 - NLP分析

**事件定义**:

```java
@Getter
@AllArgsConstructor
public class FeedbackSubmittedEvent {
    private final Long feedbackId;
    private final String content;
    private final Long activityId;
}
```

**发布事件**:

```java
@Service
@RequiredArgsConstructor
public class FeedbackService {

    private final FeedbackRepository feedbackRepository;
    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public FeedbackDTO submitFeedback(FeedbackRequest request, Long userId) {
        Feedback feedback = new Feedback();
        feedback.setActivityId(request.getActivityId());
        feedback.setUserId(userId);
        feedback.setRating(request.getRating());
        feedback.setContent(request.getContent());
        feedback.setAnalysisStatus(AnalysisStatus.PENDING);

        Feedback saved = feedbackRepository.save(feedback);

        // 发布事件，异步触发NLP分析
        eventPublisher.publishEvent(new FeedbackSubmittedEvent(
            saved.getId(),
            saved.getContent(),
            saved.getActivityId()
        ));

        return FeedbackMapper.toDTO(saved);
    }
}
```

**监听事件**:

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class FeedbackEventListener {

    private final AlgorithmService algorithmService;
    private final FeedbackRepository feedbackRepository;

    @Async
    @EventListener
    public void handleFeedbackSubmitted(FeedbackSubmittedEvent event) {
        log.info("开始NLP分析, feedbackId={}", event.getFeedbackId());

        try {
            Feedback feedback = feedbackRepository.findById(event.getFeedbackId())
                    .orElseThrow(() -> new NotFoundException("反馈不存在"));

            // 调用Python NLP服务
            NLPAnalysisResult result = algorithmService.analyzeSentiment(event.getContent());

            // 更新分析结果
            feedback.setSentimentScore(result.getSentimentScore());
            feedback.setSentimentLevel(result.getSentimentLevel());
            feedback.setKeywords(result.getKeywords());
            feedback.setAspectSentiments(result.getAspectSentiments());
            feedback.setAnalysisStatus(AnalysisStatus.ANALYZED);
            feedback.setAnalyzedAt(LocalDateTime.now());

            feedbackRepository.save(feedback);
            log.info("NLP分析完成, feedbackId={}", event.getFeedbackId());

        } catch (Exception e) {
            log.error("NLP分析失败, feedbackId={}", event.getFeedbackId(), e);

            feedbackRepository.findById(event.getFeedbackId()).ifPresent(feedback -> {
                feedback.setAnalysisStatus(AnalysisStatus.FAILED);
                feedbackRepository.save(feedback);
            });
        }
    }
}
```

---

## 常见问题

### Q1: 如何解决循环依赖？

**方案A**: 使用 `@Lazy` 延迟加载

```java
@Service
@RequiredArgsConstructor
public class ClubService {
    private final @Lazy ActivityService activityService;
}
```

**方案B**: 重构，将公共逻辑抽取到第三个服务

### Q2: 如何处理大数据量分页？

```java
@Query(value = "SELECT * FROM activities WHERE status = :status",
       countQuery = "SELECT count(*) FROM activities WHERE status = :status",
       nativeQuery = true)
Page<Activity> findByStatusNative(@Param("status") String status, Pageable pageable);
```

### Q3: 如何实现软删除？

```java
@Entity
@Where(clause = "deleted = false")
@FilterDef(name = "deletedFilter", parameters = @ParamDef(name = "deleted", type = Boolean.class))
@Filter(name = "deletedFilter", condition = "deleted = :deleted")
public class Activity {
    // ...
    private boolean deleted = false;
}
```

### Q4: 如何优化N+1查询？

```java
@EntityGraph(attributePaths = {"club", "participants"})
@Query("SELECT a FROM Activity a WHERE a.status = :status")
List<Activity> findByStatusWithRelations(@Param("status") ActivityStatus status);
```

---

## 测试指南

### 单元测试

```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    @WithMockUser(roles = "ADMIN")
    void shouldCreateUser() throws Exception {
        // given
        when(userService.createUser(any())).thenReturn(new UserDTO());

        // when & then
        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{"username":"test","password":"123456"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }
}
```

### 集成测试

```java
@SpringBootTest
@Testcontainers
class ActivityIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:14");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Test
    void shouldCompleteActivityWorkflow() {
        // 完整的业务流程测试
    }
}
```
