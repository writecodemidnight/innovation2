# 校园社团活动评估系统 - 后端架构设计文档

## 项目概述

### 1.1 项目名称
基于大数据分析的校园社团活动效果评估与资源优化配置系统

### 1.2 项目目标
构建一个"数据采集 - 效果评估 - 资源优化"的一体化系统，通过整合多源数据并运用大数据分析和人工智能算法，客观量化活动质量，实现校园资源的智能调度与优化配置。

### 1.3 核心需求
- **学生端**：个性化活动推荐、活动报名与参与记录、活动效果评价
- **社团端**：活动申报与策划书提交、资源预约申请、效果分析报告查询
- **管理端**：多源数据监控大屏、资源池管理、智能审批与决策
- **后台算法**：多源数据融合、五维评估模型、资源需求预测与优化调度

## 技术栈选型

### 2.1 后端技术栈
- **核心框架**：Spring Boot 3.2.x (Java 17)
- **构建工具**：Maven 3.9+ 或 Gradle 8.5+
- **关键依赖**：
  - Spring Security (JWT认证 + OAuth2客户端)
  - Spring Data JPA (数据库ORM)
  - Spring Boot Actuator (健康检查)
  - MapStruct (对象映射)
  - Lombok (减少样板代码)

### 2.2 算法服务
- **核心框架**：Python 3.10+ + FastAPI 0.104+
- **算法库**：
  - scikit-learn (K-Means聚类、AHP层次分析)
  - pandas/numpy (数据处理)
  - tensorflow/pytorch (LSTM时间序列预测)
  - OpenCV (计算机视觉分析)
  - nltk/spaCy (NLP情感分析)

### 2.3 数据存储
- **主数据库**：PostgreSQL 15.x (支持JSONB和窗口函数)
- **缓存层**：Redis 7.2.x (会话管理、热点数据缓存)
- **对象存储**：阿里云OSS (文件存储)

### 2.4 基础设施
- **容器化**：Docker 24.x + Docker Compose v2.23+
- **云服务**：阿里云ECS (4核8G Ubuntu 22.04)
- **CI/CD**：GitHub Actions 或 Gitee Go
- **监控**：Spring Boot Admin + Prometheus + Grafana

## 架构设计

### 3.1 总体架构
采用**混合架构**方案：核心业务单体 + 独立算法服务

```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (Vue.js + Uni-app)                   │
│                小程序端 ↔ PC端 双端适配                       │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS + JWT
┌─────────────────▼───────────────────────────────────────────┐
│               Spring Boot 核心业务单体                        │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐       │
│  │ 用户模块 │ 活动模块 │ 资源模块 │ 评估模块 │ 管理模块 │       │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘       │
└─────────────────┬───────────────────────────────────────────┘
                  │ REST API (JSON)
┌─────────────────▼───────────────────────────────────────────┐
│               Python FastAPI 算法服务                        │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┐        │
│  │K-Means│  AHP  │ LSTM │ GA   │ NLP  │ CV   │Apriori│        │
│  └──────┴──────┴──────┴──────┴──────┴──────┴──────┘        │
└─────────────────┬───────────────────────────────────────────┘
                  │ 数据访问
┌─────────────────▼───────────────────────────────────────────┐
│                 数据存储层                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │   Redis     │  │  阿里云 OSS  │        │
│  │ (主数据库)   │  │  (缓存)     │  │ (文件存储)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 架构优势
1. **适合小团队**：5人团队可快速上手，减少分布式系统复杂性
2. **技术栈隔离**：Java擅长业务逻辑，Python擅长算法，各取所长
3. **渐进式演进**：未来如需拆分，可从单体中逐步剥离服务
4. **成本可控**：基础设施简单，云服务器成本可控

## 模块划分

### 4.1 Java核心业务单体模块

#### 4.1.1 用户模块 (`user-service`)
- **职责**：用户注册、登录、个人信息管理、权限控制
- **核心类**：`UserController`, `UserService`, `UserRepository`, `WechatAuthService`
- **数据库表**：`users`, `user_roles`, `permissions`

#### 4.1.2 活动模块 (`activity-service`)
- **职责**：活动创建、审批、查询、报名、记录
- **核心类**：`ActivityController`, `ActivityService`, `ActivityRepository`, `ActivityRecommendationService`
- **数据库表**：`activities`, `activity_participants`, `activity_resources`

#### 4.1.3 资源模块 (`resource-service`)
- **职责**：场地、设备、经费的资源池管理、预约、分配
- **核心类**：`ResourceController`, `ResourceService`, `ResourceOptimizationService`, `ResourceRepository`
- **数据库表**：`resources`, `resource_reservations`, `resource_budgets`

#### 4.1.4 评估模块 (`evaluation-service`)
- **职责**：收集评价、计算基础指标、生成报告
- **核心类**：`EvaluationController`, `EvaluationService`, `ReportGeneratorService`, `EvaluationRepository`
- **数据库表**：`evaluations`, `evaluation_metrics`, `activity_reports`

#### 4.1.5 管理模块 (`admin-service`)
- **职责**：数据看板、审批流程、系统配置
- **核心类**：`AdminController`, `DashboardService`, `ApprovalWorkflowService`, `SystemConfigService`
- **数据库表**：`approval_records`, `system_configs`, `operation_logs`

### 4.2 Python算法服务API设计

#### 4.2.1 基础信息
- **服务URL**：`http://algorithm-service:8000/api/v1`
- **通信协议**：REST API (JSON格式)
- **超时设置**：默认30秒
- **重试策略**：指数退避，最多3次

#### 4.2.2 算法接口

| 端点 | 方法 | 输入 | 输出 | 用途 |
|------|------|------|------|------|
| `/recommend/kmeans` | POST | `{user_id, history_activities, top_n}` | `{recommended_activities: [...]}` | K-Means个性化推荐 |
| `/evaluation/ahp` | POST | `{activity_id, metrics_data, weights}` | `{scores: {...}, radar_data: {...}}` | AHP层次分析法评估 |
| `/nlp/sentiment` | POST | `{texts: ["text1", "text2"]}` | `{sentiments: [score1, score2]}` | NLP情感分析 |
| `/prediction/lstm` | POST | `{historical_demand, time_features}` | `{predicted_demand: [...]}` | LSTM资源需求预测 |
| `/optimization/ga` | POST | `{activities, resources, constraints}` | `{allocation_plan: {...}}` | 遗传算法资源优化 |
| `/mining/apriori` | POST | `{transactions: [...]}` | `{rules: [...]}` | Apriori关联规则挖掘 |
| `/cv/quality` | POST | `{image_urls: [...]}` | `{quality_scores: [...]}` | CV活动现场图片质量分析 |

## 数据库设计

### 5.1 核心实体关系

#### 5.1.1 用户与角色（RBAC）
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    openid VARCHAR(100) UNIQUE,  -- 微信OpenID
    username VARCHAR(50) NOT NULL,
    avatar_url VARCHAR(255),
    email VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'STUDENT', -- STUDENT, CLUB_ADMIN, SYS_ADMIN
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.1.2 社团管理
```sql
CREATE TABLE clubs (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- 学术、文艺、体育、公益等
    logo_url VARCHAR(255),
    president_id BIGINT REFERENCES users(id),
    faculty_advisor VARCHAR(100),
    status VARCHAR(20) DEFAULT 'ACTIVE', -- ACTIVE, INACTIVE, SUSPENDED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.1.3 活动相关
```sql
CREATE TABLE activities (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    activity_type VARCHAR(50), -- lecture, workshop, competition, social
    status VARCHAR(20) DEFAULT 'DRAFT', -- DRAFT, PENDING, APPROVED, REJECTED, COMPLETED
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location VARCHAR(200),
    capacity INT,
    current_participants INT DEFAULT 0,
    club_id BIGINT REFERENCES clubs(id),
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (end_time > start_time)
);
```

#### 5.1.4 资源管理
```sql
CREATE TABLE resources (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- VENUE, EQUIPMENT, BUDGET
    capacity INT,
    unit VARCHAR(20), -- 单位：人、个、元
    available_count INT DEFAULT 0,
    total_count INT NOT NULL,
    constraints JSONB, -- 约束条件，如时间限制、使用规则
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.1.5 五维评估指标
```sql
CREATE TABLE evaluation_metrics (
    activity_id BIGINT PRIMARY KEY REFERENCES activities(id),
    participation_score DECIMAL(5,2),  -- 参与度
    educational_score DECIMAL(5,2),    -- 教育性
    innovation_score DECIMAL(5,2),     -- 创新性
    influence_score DECIMAL(5,2),      -- 影响力
    sustainability_score DECIMAL(5,2), -- 可持续性
    overall_score DECIMAL(5,2),        -- 综合得分（AHP计算）
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 索引优化策略
- `activities(start_time, status)`：活动时间查询
- `activity_participants(activity_id, status)`：参与状态查询
- `resources(type, available_count)`：资源筛选
- `users(openid)`：微信登录快速查询

## 安全设计

### 6.1 认证体系
- **JWT Token**：采用HS256算法，有效期2小时
- **Refresh Token**：有效期7天，用于获取新Access Token
- **Token黑名单**：Redis存储已注销但未过期的Token

### 6.2 微信OAuth2.0集成
```
1. 前端重定向 → 微信授权页面
2. 用户授权 → 返回code
3. 后端用code + appsecret → 换取access_token和openid
4. 验证openid → 生成JWT返回前端
5. 前端存储JWT → 后续请求携带Authorization头
```

### 6.3 RBAC权限模型
- **角色层级**：SUPER_ADMIN, DEPARTMENT_ADMIN, CLUB_ADMIN, STUDENT
- **权限粒度**：activity:create/read/update/delete/approve, resource:reserve/allocate/manage, user:manage/assign_role, evaluation:submit/view_report

### 6.4 API安全防护
- **SQL注入防护**：使用JPA参数化查询
- **XSS防护**：输入输出过滤，Content-Type检查
- **CSRF防护**：前后端分离架构天然防御
- **限流防刷**：Redis实现接口限流（如登录接口60次/小时）
- **敏感数据脱敏**：返回数据时屏蔽手机号、邮箱等敏感信息

## 部署架构

### 7.1 Docker Compose编排

```yaml
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
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    container_name: campus-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

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

### 7.2 云服务器部署结构
```
阿里云ECS (4核8G Ubuntu 22.04)
├── /opt/campus-club/
│   ├── docker-compose.yml
│   ├── .env (环境变量，不提交到Git)
│   ├── campus-main/ (Java应用)
│   ├── campus-ai/ (Python算法服务)
│   └── logs/ (统一日志目录)
├── Nginx (反向代理，配置SSL证书)
└── 阿里云OSS (文件存储)
```

### 7.3 CI/CD流水线
- **触发条件**：main分支push或手动触发
- **构建阶段**：Java编译打包、Docker镜像构建、推送镜像仓库
- **部署阶段**：SSH连接到ECS，拉取最新镜像，重启服务
- **监控阶段**：健康检查，失败自动回滚

## 监控与运维

### 8.1 日志收集
- **应用日志**：Logback配置JSON格式，按天滚动
- **访问日志**：Nginx日志，包含请求时间、响应码、处理时长
- **错误追踪**：Sentry集成，实时告警

### 8.2 监控指标
- **应用健康**：Spring Boot Actuator `/actuator/health`
- **性能监控**：Prometheus收集JVM、HTTP请求、数据库连接池指标
- **业务监控**：自定义指标（活动创建数、用户活跃度、算法调用成功率）

### 8.3 告警规则
- 服务响应时间 > 5s
- 错误率 > 5%
- 内存使用率 > 80%
- 算法服务不可用 > 5分钟

### 8.4 备份策略
- **数据库备份**：每天凌晨2点全量备份，保留7天
- **配置文件备份**：Git版本控制
- **OSS文件备份**：阿里云跨区域复制（可选）

## 实施计划

### 9.1 第一阶段：基础框架搭建（1-2周）
1. Spring Boot项目初始化
2. 基础依赖配置（Spring Security, JPA, Redis等）
3. Docker环境配置
4. 数据库表结构创建

### 9.2 第二阶段：核心业务实现（3-4周）
1. 用户模块（微信登录、RBAC权限）
2. 活动模块（CRUD、状态流转）
3. 资源模块（资源池管理、预约逻辑）
4. 基础API接口开发

### 9.3 第三阶段：算法服务集成（2-3周）
1. Python FastAPI服务搭建
2. 核心算法实现（K-Means, AHP, LSTM等）
3. 服务间通信集成
4. 算法结果缓存优化

### 9.4 第四阶段：系统优化与部署（1-2周）
1. 性能调优与压力测试
2. 安全加固
3. 生产环境部署
4. 监控告警配置

## 风险评估与应对

### 10.1 技术风险
- **算法性能问题**：遗传算法计算复杂可能导致响应慢
  - 应对：结果缓存、异步计算、算法优化
- **服务间通信延迟**：Java与Python服务网络调用延迟
  - 应对：连接池优化、批量请求、降级方案

### 10.2 团队风险
- **技术栈多样性**：Java + Python双技术栈学习成本
  - 应对：明确分工、文档完善、代码规范
- **分布式系统复杂性**：小团队处理分布式问题经验不足
  - 应对：采用混合架构，避免过早微服务化

### 10.3 运维风险
- **云服务器成本**：算法服务内存需求高，可能导致费用增加
  - 应对：资源监控、自动伸缩、成本优化
- **数据安全**：学生个人信息保护
  - 应对：数据脱敏、访问控制、审计日志

## 附录

### A.1 环境变量配置示例
```bash
# ============================================
# 重要：以下值为示例，实际部署时需要替换为真实值
# ============================================

# 数据库配置（PostgreSQL）
DB_HOST=postgres                    # Docker Compose中的服务名
DB_PORT=5432                        # PostgreSQL默认端口
DB_NAME=campus_club                 # 数据库名称
DB_USER=campus_user                 # 数据库用户名
DB_PASSWORD=change_me_secure_password_123  # 强密码，需替换

# Redis配置
REDIS_HOST=redis                    # Docker Compose中的服务名
REDIS_PORT=6379                     # Redis默认端口
REDIS_PASSWORD=change_me_redis_password_456  # Redis密码，需替换

# 微信开放平台配置（需申请）
WECHAT_APP_ID=wx1234567890abcdef    # 微信小程序/公众号AppID
WECHAT_SECRET=your_wechat_app_secret_here  # 微信AppSecret

# 阿里云OSS配置（需开通服务）
ALIYUN_ACCESS_KEY=your_aliyun_access_key_here      # 阿里云AccessKey
ALIYUN_SECRET_KEY=your_aliyun_secret_key_here      # 阿里云SecretKey
OSS_BUCKET_NAME=campus-club-files-{env}           # OSS存储桶名称，{env}替换为环境标识

# 可选：Sentry错误监控（可选）
SENTRY_DSN=https://your_sentry_dsn_here@sentry.io/your_project_id
```

### A.2 项目目录结构
```
campus-club-backend/
├── campus-main/                    # Java核心业务
│   ├── src/main/java/
│   │   ├── com/campusclub/
│   │   │   ├── user/              # 用户模块
│   │   │   ├── activity/          # 活动模块
│   │   │   ├── resource/          # 资源模块
│   │   │   ├── evaluation/        # 评估模块
│   │   │   ├── admin/             # 管理模块
│   │   │   └── config/            # 配置类
│   │   └── resources/
│   │       ├── application.yml    # 主配置文件
│   │       └── db/migration/      # 数据库迁移脚本
│   └── Dockerfile
│
├── campus-ai/                      # Python算法服务
│   ├── src/
│   │   ├── algorithms/
│   │   │   ├── recommendation/    # 推荐算法
│   │   │   ├── evaluation/        # 评估算法
│   │   │   ├── prediction/        # 预测算法
│   │   │   └── optimization/      # 优化算法
│   │   └── api/                   # FastAPI接口
│   ├── requirements.txt           # Python依赖
│   └── Dockerfile
│
├── docker-compose.yml              # 容器编排
├── .env.example                    # 环境变量示例
└── docs/                           # 文档
    └── superpowers/specs/          # 设计文档（当前文件位置）
```

---
*文档版本：1.0*
*最后更新：2026-04-09*
*设计者：Claude Code*
*状态：已批准*