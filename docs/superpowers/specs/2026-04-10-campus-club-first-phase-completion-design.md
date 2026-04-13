# 校园社团活动评估系统 - 第一阶段完善设计文档

## 项目概述

### 1.1 项目名称
基于大数据分析的校园社团活动效果评估与资源优化配置系统

### 1.2 完善目标
完成第一阶段"基建与架构设计"中未完成的各项任务，确保系统具备完整的开发基础和标准化规范，为后续开发奠定坚实基础。

### 1.3 完善范围
1. **技术栈确认与环境搭建**：验证现有技术栈，补充环境配置
2. **数据仓库模型设计**：在PostgreSQL中实现混合数据仓库架构
3. **API接口定义**：完成前后端、服务间API标准化
4. **ETL流程设计**：业务数据到分析数据的同步机制
5. **防御性编程**：系统健壮性保障措施

## 技术栈确认与环境搭建完善

### 2.1 当前状态验证

#### 2.1.1 后端技术栈 ✅
- **核心框架**：Spring Boot 3.2.5 + Java 17
- **构建工具**：Maven + Maven Wrapper（mvnw）
- **关键依赖**：Spring Security, Spring Data JPA, Spring Boot Actuator
- **数据库**：PostgreSQL 15.x（已配置Flyway迁移）
- **缓存**：Redis（已配置连接）

#### 2.1.2 算法服务 ✅
- **核心框架**：Python 3.10+ + FastAPI 0.104.1
- **算法库**：scikit-learn 1.4.0, pandas 2.2.0, numpy 1.26.4, torch 2.4.0
- **数据处理**：已实现DataProcessor数据清洗类

#### 2.1.3 前端技术栈 ✅
- **框架**：Vue 3 + uni-app（支持小程序/H5/PC多端）
- **构建工具**：Vite 5.2.8 + TypeScript 6.0.2
- **UI框架**：uview-ui 2.0.38

### 2.2 环境配置补充

#### 2.2.1 Docker Compose编排
```yaml
# docker-compose.yml - 统一环境编排
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: campus-postgres
    environment:
      POSTGRES_DB: campus_club
      POSTGRES_USER: campus_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d  # 初始化脚本
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U campus_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: campus-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  java-app:
    build:
      context: ./campus-main
      dockerfile: Dockerfile
    container_name: campus-java
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DB_HOST: postgres
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_HOST: redis
      ALGORITHM_SERVICE_URL: http://algorithm-service:8000
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  algorithm-service:
    build:
      context: ./campus-ai
      dockerfile: Dockerfile
    container_name: campus-algorithm
    environment:
      PYTHONPATH: /app
      MODEL_CACHE_DIR: /app/models
      REDIS_HOST: redis
      DB_CONNECTION_STRING: postgresql://campus_user:${DB_PASSWORD}@postgres:5432/campus_club
    ports:
      - "8000:8000"
    volumes:
      - ./ai-models:/app/models
    deploy:
      resources:
        limits:
          memory: 4G

volumes:
  postgres_data:
  redis_data:
```

#### 2.2.2 环境变量模板
```bash
# .env.example
# ============================================
# 数据库配置
# ============================================
DB_HOST=postgres
DB_PORT=5432
DB_NAME=campus_club
DB_USER=campus_user
DB_PASSWORD=change_me_secure_password_123

# ============================================
# Redis配置
# ============================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=change_me_redis_password_456

# ============================================
# 算法服务配置
# ============================================
ALGORITHM_SERVICE_URL=http://algorithm-service:8000
ALGORITHM_TIMEOUT_SECONDS=30
ALGORITHM_RETRY_COUNT=3

# ============================================
# 微信开放平台（开发阶段可选）
# ============================================
WECHAT_APP_ID=your_wechat_app_id
WECHAT_SECRET=your_wechat_secret

# ============================================
# 阿里云OSS（开发阶段可选）
# ============================================
ALIYUN_ACCESS_KEY=your_access_key
ALIYUN_SECRET_KEY=your_secret_key
OSS_BUCKET_NAME=campus-club-dev
```

## 数据仓库模型设计（混合模型）

### 3.1 架构设计理念
采用"物理同库、逻辑隔离"的混合模型，在PostgreSQL中创建独立的`analytics`模式，实现业务数据与分析数据的逻辑隔离，避免维护两个数据库集群的成本。

### 3.2 分析模式表结构

#### 3.2.1 核心分析表
```sql
-- 创建分析模式
CREATE SCHEMA IF NOT EXISTS analytics;

-- 活动分析事实表
CREATE TABLE analytics.activity_facts (
    activity_id BIGINT PRIMARY KEY,
    club_id BIGINT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    start_hour INTEGER NOT NULL,
    duration_hours DECIMAL(5,2) NOT NULL,
    participant_count INTEGER NOT NULL DEFAULT 0,
    resource_count INTEGER NOT NULL DEFAULT 0,
    avg_feedback_score DECIMAL(3,2),
    total_budget DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 资源使用分析表（LSTM算法数据源）
CREATE TABLE analytics.resource_utilization (
    resource_id BIGINT NOT NULL,
    date DATE NOT NULL,
    utilization_hours DECIMAL(5,2) NOT NULL DEFAULT 0,
    reservation_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (resource_id, date)
);

-- 用户参与分析表  
CREATE TABLE analytics.user_participation (
    user_id BIGINT NOT NULL,
    month DATE NOT NULL,
    activity_count INTEGER NOT NULL DEFAULT 0,
    avg_rating DECIMAL(3,2),
    participation_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, month)
);
```

#### 3.2.2 高性能索引设计
```sql
-- 复合索引优化：LSTM算法查询加速
CREATE INDEX idx_resource_utilization_date_resource 
ON analytics.resource_utilization(date, resource_id);

CREATE INDEX idx_activity_facts_club_date 
ON analytics.activity_facts(club_id, start_date);

CREATE INDEX idx_activity_facts_type_date 
ON analytics.activity_facts(activity_type, start_date);

CREATE INDEX idx_user_participation_month_score 
ON analytics.user_participation(month, participation_score DESC);
```

### 3.3 物化视图设计

#### 3.3.1 关键分析视图
```sql
-- 社团活动月度统计（支持并发刷新）
CREATE MATERIALIZED VIEW analytics.club_monthly_stats AS
SELECT 
    club_id,
    DATE_TRUNC('month', start_date) as month,
    COUNT(*) as total_activities,
    AVG(participant_count) as avg_participants,
    SUM(resource_count) as total_resources_used,
    AVG(avg_feedback_score) as avg_feedback
FROM analytics.activity_facts
GROUP BY club_id, DATE_TRUNC('month', start_date);

-- 资源类型使用率分析
CREATE MATERIALIZED VIEW analytics.resource_type_analysis AS
SELECT
    r.resource_type,
    DATE_TRUNC('week', ru.date) as week,
    AVG(ru.utilization_hours) as avg_utilization,
    COUNT(DISTINCT ru.resource_id) as active_resources,
    SUM(ru.reservation_count) as total_reservations
FROM analytics.resource_utilization ru
JOIN public.resources r ON ru.resource_id = r.id
GROUP BY r.resource_type, DATE_TRUNC('week', ru.date);
```

#### 3.3.2 物化视图刷新机制
由于PostgreSQL原生不支持自动刷新，采用Spring Boot调度任务：

```java
@Component
@Slf4j
public class MaterializedViewScheduler {
    
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @Scheduled(cron = "0 0 */2 * * *") // 每2小时刷新一次
    public void refreshMaterializedViews() {
        log.info("开始刷新物化视图...");
        
        try {
            // 使用CONCURRENTLY避免查询锁死
            jdbcTemplate.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.club_monthly_stats");
            jdbcTemplate.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.resource_type_analysis");
            
            log.info("物化视图刷新完成");
        } catch (Exception e) {
            log.error("物化视图刷新失败", e);
            // 记录监控指标，不影响主业务流程
        }
    }
}
```

## ETL流程详细设计

### 4.1 ETL流程架构

```
业务数据 (Public Schema) → ETL管道 → 分析数据 (Analytics Schema)
      ↑                                      ↑
  原始交易                               聚合指标
     |                                      |
抽取(Extract) → 转换(Transform) → 加载(Load)
```

### 4.2 Spring Batch ETL作业设计

```java
@Configuration
@Slf4j
public class AnalyticsEtlConfiguration {
    
    @Bean
    public Job analyticsEtlJob(JobRepository jobRepository, Step extractStep, Step transformStep, Step loadStep) {
        return new JobBuilder("analyticsEtlJob", jobRepository)
                .start(extractStep)
                .next(transformStep)
                .next(loadStep)
                .validator(new DefaultJobParametersValidator())
                .build();
    }
    
    @Bean
    public Step extractStep(PlatformTransactionManager transactionManager, 
                           JdbcTemplate jdbcTemplate) {
        return new StepBuilder("extractStep", jobRepository)
                .<Activity, Activity>chunk(100, transactionManager)
                .reader(activityJdbcCursorItemReader(jdbcTemplate))
                .writer(activityItemWriter())
                .build();
    }
    
    private JdbcCursorItemReader<Activity> activityJdbcCursorItemReader(JdbcTemplate jdbcTemplate) {
        return new JdbcCursorItemReaderBuilder<Activity>()
                .name("activityReader")
                .dataSource(jdbcTemplate.getDataSource())
                .sql("""
                    SELECT a.*, c.club_id 
                    FROM public.activities a
                    JOIN public.clubs c ON a.club_id = c.id
                    WHERE a.status = 'COMPLETED' 
                    AND a.end_time >= CURRENT_DATE - INTERVAL '1 day'
                    """)
                .rowMapper(new BeanPropertyRowMapper<>(Activity.class))
                .build();
    }
}
```

### 4.3 增量同步SQL实现
```sql
-- 每日活动数据增量同步
INSERT INTO analytics.activity_facts (
    activity_id, club_id, activity_type, start_date, start_hour, 
    duration_hours, participant_count, resource_count, avg_feedback_score, total_budget
)
SELECT 
    a.id as activity_id,
    a.club_id,
    a.activity_type,
    DATE(a.start_time) as start_date,
    EXTRACT(HOUR FROM a.start_time) as start_hour,
    -- 处理跨天活动的时长计算
    CASE 
        WHEN DATE(a.end_time) = DATE(a.start_time) 
        THEN EXTRACT(EPOCH FROM (a.end_time - a.start_time)) / 3600
        ELSE 24 - EXTRACT(HOUR FROM a.start_time) + EXTRACT(HOUR FROM a.end_time)
    END as duration_hours,
    COALESCE(ap.participant_count, 0) as participant_count,
    COALESCE(rr.resource_count, 0) as resource_count,
    ROUND(AVG(ap.rating) FILTER (WHERE ap.rating IS NOT NULL), 2) as avg_feedback_score,
    COALESCE(a.budget_amount, 0) as total_budget
FROM public.activities a
LEFT JOIN (
    SELECT activity_id, COUNT(*) as participant_count, AVG(rating) as avg_rating
    FROM public.activity_participants
    WHERE participation_status = 'CHECKED_OUT'
    GROUP BY activity_id
) ap ON a.id = ap.activity_id
LEFT JOIN (
    SELECT activity_id, COUNT(*) as resource_count
    FROM public.resource_reservations
    WHERE status = 'APPROVED'
    GROUP BY activity_id
) rr ON a.id = rr.activity_id
WHERE a.status = 'COMPLETED'
    AND a.end_time >= CURRENT_DATE - INTERVAL '1 day'
    AND NOT EXISTS (
        SELECT 1 FROM analytics.activity_facts af 
        WHERE af.activity_id = a.id
    )
GROUP BY a.id, a.club_id, a.activity_type, a.start_time, a.end_time, a.budget_amount;

-- 数据质量校验
SELECT 
    '活动数据完整性' as check_name,
    COUNT(*) as source_count,
    (SELECT COUNT(*) FROM analytics.activity_facts WHERE start_date = CURRENT_DATE - 1) as target_count,
    CASE 
        WHEN COUNT(*) = (SELECT COUNT(*) FROM analytics.activity_facts WHERE start_date = CURRENT_DATE - 1)
        THEN 'PASS' 
        ELSE 'FAIL' 
    END as result
FROM public.activities 
WHERE status = 'COMPLETED' 
    AND DATE(end_time) = CURRENT_DATE - 1;
```

## API接口定义与标准化

### 5.1 Swagger配置完善

#### 5.1.1 添加SpringDoc依赖
```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.5.0</version>
</dependency>
```

#### 5.1.2 Swagger配置类
```java
@Configuration
@OpenAPIDefinition(
    info = @Info(
        title = "校园社团活动评估系统API",
        version = "1.0.0",
        description = "基于大数据分析的校园社团活动效果评估与资源优化配置系统",
        contact = @Contact(name = "开发团队", email = "dev@campus.edu")
    ),
    servers = {
        @Server(url = "http://localhost:8080", description = "本地开发环境"),
        @Server(url = "https://api.campus.edu", description = "生产环境")
    },
    externalDocs = @ExternalDocumentation(
        description = "详细文档",
        url = "https://docs.campus.edu"
    )
)
public class OpenApiConfig {
    
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .addSecurityItem(new SecurityRequirement().addList("JWT"))
                .components(new Components()
                        .addSecuritySchemes("JWT", new SecurityScheme()
                                .type(SecurityScheme.Type.HTTP)
                                .scheme("bearer")
                                .bearerFormat("JWT")
                                .description("JWT认证Token")))
                .tags(List.of(
                    new Tag().name("用户管理").description("用户注册、登录、个人信息接口"),
                    new Tag().name("活动管理").description("活动创建、查询、报名接口"),
                    new Tag().name("资源管理").description("资源预约、分配、管理接口"),
                    new Tag().name("算法服务").description("内部算法接口，供Java服务调用").extensions(
                        Map.of("x-internal", true)  // 标记为内部API
                    ),
                    new Tag().name("分析数据").description("数据分析与报表接口")
                ));
    }
}
```

### 5.2 控制器架构标准化

```
campus-main/src/main/java/com/campusclub/
├── controller/
│   ├── UserController.java          # 用户管理接口（外部API）
│   ├── ActivityController.java      # 活动管理接口（外部API）
│   ├── ResourceController.java      # 资源管理接口（外部API）
│   ├── EvaluationController.java    # 评估接口（外部API）
│   ├── AdminController.java         # 管理接口（外部API）
│   └── internal/
│       ├── AlgorithmProxyController.java  # 算法代理接口（内部API）
│       └── AnalyticsController.java       # 分析数据接口（内部API）
```

### 5.3 统一响应格式
```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponse<T> {
    private boolean success;
    private String code;
    private String message;
    private T data;
    private Long timestamp;
    
    public static <T> ApiResponse<T> success(T data) {
        return ApiResponse.<T>builder()
                .success(true)
                .code("SUCCESS")
                .message("操作成功")
                .data(data)
                .timestamp(System.currentTimeMillis())
                .build();
    }
    
    public static ApiResponse<?> error(String code, String message) {
        return ApiResponse.builder()
                .success(false)
                .code(code)
                .message(message)
                .timestamp(System.currentTimeMillis())
                .build();
    }
}
```

### 5.4 内部API设计（Java ↔ Python）

#### 5.4.1 算法服务数据协议
```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AlgorithmRequest {
    @Schema(description = "算法类型: KMEANS, AHP, LSTM, GA, NLP, CV")
    private String algorithmType;
    
    @Schema(description = "请求参数，根据算法类型变化")
    private Map<String, Object> parameters;
    
    @Schema(description = "数据源表名（analytics模式）")
    private String dataSourceTable;
    
    @Schema(description = "数据字段映射，确保Python读取的字段名与数据库一致")
    private Map<String, String> fieldMapping;
}

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AlgorithmResponse {
    private boolean success;
    private String algorithmType;
    private Object result;
    private Long processingTimeMs;
    private String errorMessage;
}
```

#### 5.4.2 算法代理控制器
```java
@RestController
@RequestMapping("/api/internal/algorithms")
@Tag(name = "算法服务", description = "内部算法接口，供Java服务调用")
@Slf4j
public class AlgorithmProxyController {
    
    @Autowired
    private AlgorithmService algorithmService;
    
    @PostMapping("/execute")
    @Operation(summary = "执行算法", description = "调用Python算法服务执行计算")
    @ResponseStatus(HttpStatus.OK)
    public ApiResponse<AlgorithmResponse> executeAlgorithm(
            @RequestBody @Valid AlgorithmRequest request) {
        try {
            // 设置超时和重试
            AlgorithmResponse response = algorithmService.executeWithRetry(request);
            return ApiResponse.success(response);
        } catch (AlgorithmTimeoutException e) {
            log.warn("算法执行超时: {}", request.getAlgorithmType(), e);
            return ApiResponse.error("ALGORITHM_TIMEOUT", 
                String.format("算法%s执行超时，请稍后重试", request.getAlgorithmType()));
        } catch (AlgorithmException e) {
            log.error("算法执行失败: {}", request.getAlgorithmType(), e);
            return ApiResponse.error("ALGORITHM_ERROR", 
                String.format("算法%s执行失败: %s", request.getAlgorithmType(), e.getMessage()));
        }
    }
}
```

## 防御性编程与健壮性设计

### 6.1 全局异常处理
```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {
    
    @ExceptionHandler(AlgorithmTimeoutException.class)
    @ResponseStatus(HttpStatus.GATEWAY_TIMEOUT)
    public ApiResponse<?> handleAlgorithmTimeout(AlgorithmTimeoutException e) {
        log.warn("算法服务超时: {}", e.getMessage());
        return ApiResponse.error("GATEWAY_TIMEOUT", 
            "算法服务响应超时，请稍后重试。如持续出现此问题，请联系管理员。");
    }
    
    @ExceptionHandler(HttpClientErrorException.class)
    @ResponseStatus(HttpStatus.BAD_GATEWAY)
    public ApiResponse<?> handleHttpClientError(HttpClientErrorException e) {
        log.error("HTTP客户端错误: {}", e.getMessage());
        return ApiResponse.error("SERVICE_UNAVAILABLE", 
            "依赖服务暂时不可用，请稍后重试。");
    }
    
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResponse<?> handleGenericException(Exception e) {
        log.error("系统异常: ", e);
        return ApiResponse.error("INTERNAL_ERROR", 
            "系统内部错误，请联系管理员。");
    }
}
```

### 6.2 算法服务降级策略
```java
@Service
@Slf4j
public class AlgorithmService {
    
    @Autowired
    private AlgorithmClient algorithmClient;
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    public AlgorithmResponse executeWithRetry(AlgorithmRequest request) {
        int retryCount = 0;
        int maxRetries = 3;
        long retryDelayMs = 1000;
        
        while (retryCount <= maxRetries) {
            try {
                // 尝试从缓存获取结果
                String cacheKey = generateCacheKey(request);
                AlgorithmResponse cachedResponse = getFromCache(cacheKey);
                if (cachedResponse != null) {
                    log.info("从缓存获取算法结果: {}", request.getAlgorithmType());
                    return cachedResponse;
                }
                
                // 调用算法服务
                AlgorithmResponse response = algorithmClient.execute(request);
                
                // 缓存结果（根据算法类型设置不同过期时间）
                cacheResponse(cacheKey, response, getCacheTTL(request.getAlgorithmType()));
                
                return response;
                
            } catch (TimeoutException e) {
                retryCount++;
                if (retryCount > maxRetries) {
                    throw new AlgorithmTimeoutException(
                        String.format("算法%s执行超时，重试%d次后失败", 
                        request.getAlgorithmType(), maxRetries));
                }
                
                log.warn("算法执行超时，第{}次重试", retryCount);
                try {
                    Thread.sleep(retryDelayMs * retryCount);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new AlgorithmException("重试被中断", ie);
                }
                
            } catch (Exception e) {
                throw new AlgorithmException("算法执行失败", e);
            }
        }
        
        throw new AlgorithmException("算法执行失败，已达到最大重试次数");
    }
    
    private long getCacheTTL(String algorithmType) {
        // 不同算法的缓存策略
        return switch (algorithmType) {
            case "KMEANS", "AHP" -> 3600; // 1小时
            case "LSTM", "GA" -> 1800;    // 30分钟
            default -> 600;               // 10分钟
        };
    }
}
```

### 6.3 数据一致性保障
```java
@Component
@Slf4j
public class DataConsistencyMonitor {
    
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @Scheduled(cron = "0 30 2 * * *") // 每天凌晨2:30执行
    public void checkDataConsistency() {
        log.info("开始数据一致性检查...");
        
        Map<String, ConsistencyCheck> checks = Map.of(
            "活动数据", new ConsistencyCheck(
                "SELECT COUNT(*) FROM public.activities WHERE status = 'COMPLETED'",
                "SELECT COUNT(*) FROM analytics.activity_facts"
            ),
            "资源预约", new ConsistencyCheck(
                "SELECT COUNT(*) FROM public.resource_reservations WHERE status = 'APPROVED'",
                "SELECT COUNT(DISTINCT resource_id) FROM analytics.resource_utilization"
            )
        );
        
        checks.forEach((checkName, check) -> {
            try {
                Long sourceCount = jdbcTemplate.queryForObject(check.sourceQuery, Long.class);
                Long targetCount = jdbcTemplate.queryForObject(check.targetQuery, Long.class);
                
                if (!Objects.equals(sourceCount, targetCount)) {
                    log.error("数据一致性检查失败: {} - 源数据: {}, 目标数据: {}", 
                        checkName, sourceCount, targetCount);
                    // 发送告警通知
                    sendAlert(checkName, sourceCount, targetCount);
                } else {
                    log.info("数据一致性检查通过: {}", checkName);
                }
            } catch (Exception e) {
                log.error("数据一致性检查异常: {}", checkName, e);
            }
        });
    }
    
    @Data
    @AllArgsConstructor
    private static class ConsistencyCheck {
        private String sourceQuery;
        private String targetQuery;
    }
}
```

## 实施计划与优先级

### 7.1 实施优先级
1. **P0 (立即实施)**：
   - Docker Compose环境配置
   - Swagger API文档集成
   - 全局异常处理器

2. **P1 (本周完成)**：
   - 创建analytics模式及表结构
   - 实现基础ETL同步作业
   - 算法代理控制器

3. **P2 (下周完成)**：
   - 物化视图及刷新机制
   - 数据一致性监控
   - 防御性编程完整实现

### 7.2 验证清单
- [ ] 所有服务可通过Docker Compose一键启动
- [ ] Swagger文档可正常访问并展示所有API
- [ ] 业务数据可正确同步到analytics模式
- [ ] 算法服务调用具备超时和重试机制
- [ ] 全局异常处理器可捕获并友好提示各类错误

## 风险与应对措施

### 8.1 技术风险
- **物化视图刷新锁表**：使用CONCURRENTLY选项避免
- **ETL同步性能问题**：采用分批次处理，设置合理chunk大小
- **算法服务不稳定**：实现降级策略和结果缓存

### 8.2 运维风险
- **数据不一致**：每日自动一致性检查
- **监控缺失**：集成Spring Boot Actuator和Prometheus
- **备份不完整**：配置PostgreSQL定时备份

---

*文档版本：1.0*
*最后更新：2026-04-10*
*设计者：Claude Code*
*状态：待审查*