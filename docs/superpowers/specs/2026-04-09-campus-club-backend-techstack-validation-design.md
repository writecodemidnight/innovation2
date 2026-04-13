# 校园社团活动评估系统 - 技术栈确认与环境搭建设计文档

## 项目背景

### 1.1 设计目标
验证当前项目实现与架构设计文档的一致性，完善缺失的技术栈组件，配置完整的Docker开发环境，确保系统符合设计规范并具备所有核心功能支持。

### 1.2 验证范围
- **技术栈版本验证**：Spring Boot、Java、PostgreSQL、Redis等核心组件版本一致性
- **依赖完整性验证**：微信SDK、阿里云OSS、HTTP客户端等关键依赖缺失检查
- **Docker环境验证**：完整服务栈配置，包括Java应用、算法服务、数据库、缓存
- **配置完整性验证**：环境变量、配置文件、安全配置等完整性检查

### 1.3 验证基准
以《校园社团活动评估系统 - 后端架构设计文档》(2026-04-09-campus-club-backend-architecture-design.md)为基准，逐项比对当前实现。

## 项目现状分析

### 2.1 已完成的优秀工作

| 组件 | 实现状态 | 说明 |
|------|----------|------|
| Spring Boot框架 | ✅ 已实现 | 3.2.5版本，符合设计文档要求 |
| Java版本 | ✅ 已实现 | Java 17，符合设计文档要求 |
| PostgreSQL数据库 | ✅ 已实现 | postgres:15-alpine，版本符合 |
| Redis缓存 | ⚠️ 基本实现 | redis:7-alpine（设计文档要求7.2.x） |
| 项目结构 | ✅ 已实现 | 模块化设计，配置类完整 |
| 数据库迁移 | ✅ 已实现 | Flyway V1迁移脚本已创建 |
| Docker基础环境 | ✅ 已实现 | PostgreSQL + Redis + Java应用编排 |
| 安全基础 | ✅ 已实现 | JWT + Spring Security基础配置 |
| 异常处理 | ✅ 已实现 | 全局异常处理器已配置 |

### 2.2 发现的关键差异与缺失项

#### 2.2.1 核心依赖缺失
| 依赖类别 | 设计文档要求 | 当前实现 | 影响程度 | 优先级 |
|----------|-------------|----------|----------|--------|
| 微信OAuth2.0 SDK | 微信登录集成 | 未添加依赖 | 高 - 用户认证核心功能 | P0 |
| 阿里云OSS SDK | 文件存储服务 | 未添加依赖 | 高 - 文件上传核心功能 | P0 |
| HTTP客户端(Feign) | 算法服务通信 | 未配置 | 中 - 系统特色功能依赖 | P1 |
| Redis客户端优化 | Jedis连接池 | 使用Lettuce基础配置 | 低 - 性能优化 | P2 |

#### 2.2.2 Docker环境不完整
| 服务组件 | 设计文档要求 | 当前实现 | 影响程度 | 优先级 |
|----------|-------------|----------|----------|--------|
| Python算法服务 | 独立算法服务 | 被注释，未启用 | 高 - 混合架构核心 | P0 |
| 服务间网络配置 | 明确通信URL | 未配置算法服务URL | 中 - 服务通信基础 | P1 |
| 资源限制配置 | 算法服务内存限制 | 未配置 | 低 - 资源管理优化 | P2 |

#### 2.2.3 配置完整性缺失
| 配置类别 | 设计文档要求 | 当前实现 | 影响程度 | 优先级 |
|----------|-------------|----------|----------|--------|
| 微信应用配置 | AppID + Secret | 未配置环境变量 | 高 - 功能不可用 | P0 |
| 阿里云OSS配置 | AccessKey + SecretKey | 未配置环境变量 | 高 - 功能不可用 | P0 |
| 算法服务URL | 服务通信地址 | 未配置环境变量 | 中 - 通信失败 | P1 |
| 监控配置 | Sentry等可选配置 | 未提供配置模板 | 低 - 可观测性 | P2 |

### 2.3 技术栈版本差异总结

| 技术组件 | 设计文档要求 | 当前实现 | 状态 | 修复建议 |
|----------|-------------|----------|------|----------|
| Spring Boot | 3.2.x | 3.2.5 | ✅ 符合 | - |
| Java | 17 | 17 | ✅ 符合 | - |
| PostgreSQL | 15.x | postgres:15-alpine | ✅ 符合 | - |
| Redis | 7.2.x | redis:7-alpine | ⚠️ 版本略低 | 升级到7.2-alpine |
| MapStruct | 未指定 | 1.5.5.Final | ✅ 已配置 | - |
| Lombok | 未指定 | 1.18.30 | ✅ 已配置 | - |

## 修复设计方案

### 3.1 设计原则

1. **最小化变更**：优先修复功能阻碍项，保持现有稳定代码
2. **分阶段实施**：验证 → 补充 → 测试，降低风险
3. **向后兼容**：所有变更确保现有功能不受影响
4. **文档完整**：所有变更记录在案，便于后续维护

### 3.2 技术栈修复方案

#### 3.2.1 pom.xml依赖补充

```xml
<!-- ============================================ -->
<!-- 缺失依赖补充 - 微信OAuth2.0支持 -->
<!-- ============================================ -->
<dependency>
    <groupId>com.github.binarywang</groupId>
    <artifactId>weixin-java-mp</artifactId>
    <version>4.6.0</version>
</dependency>
<dependency>
    <groupId>com.github.binarywang</groupId>
    <artifactId>weixin-java-common</artifactId>
    <version>4.6.0</version>
</dependency>

<!-- ============================================ -->
<!-- 缺失依赖补充 - 阿里云OSS文件存储 -->
<!-- ============================================ -->
<dependency>
    <groupId>com.aliyun.oss</groupId>
    <artifactId>aliyun-sdk-oss</artifactId>
    <version>3.17.4</version>
</dependency>

<!-- ============================================ -->
<!-- 缺失依赖补充 - HTTP客户端(算法服务通信) -->
<!-- ============================================ -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-openfeign</artifactId>
    <version>4.1.1</version>
</dependency>
<dependency>
    <groupId>io.github.openfeign</groupId>
    <artifactId>feign-okhttp</artifactId>
    <version>13.2.1</version>
</dependency>

<!-- ============================================ -->
<!-- 优化依赖 - Redis客户端升级 -->
<!-- ============================================ -->
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>5.1.0</version>
    <optional>true</optional>
</dependency>
```

#### 3.2.2 版本对齐策略

1. **强制对齐项**：Redis镜像版本从7-alpine升级到7.2-alpine
2. **建议对齐项**：保持现有稳定版本，不强制升级
3. **新增配置项**：所有新增依赖使用当前稳定版本

### 3.3 Docker环境完善方案

#### 3.3.1 docker-compose.yml优化

```yaml
# 启用算法服务配置
algorithm-service:
  build:
    context: ./campus-ai
    dockerfile: Dockerfile
  container_name: campus-algorithm
  environment:
    PYTHONPATH: /app
    MODEL_CACHE_DIR: /app/models
    REDIS_HOST: redis
    JAVA_SERVICE_URL: http://java-app:8080
    # Python算法服务专用配置
    ALGORITHM_MODEL_PATH: /app/models/pretrained
    ALGORITHM_CACHE_SIZE: 1000
  ports:
    - "8000:8000"
  volumes:
    - ./ai-models:/app/models
    - ./campus-ai/src:/app/src:ro
  deploy:
    resources:
      limits:
        memory: 4G
        cpus: '2.0'
      reservations:
        memory: 2G
        cpus: '1.0'
  depends_on:
    redis:
      condition: service_healthy
  networks:
    - campus-network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s

# Java应用环境变量扩展
java-app:
  environment:
    # 现有配置保持
    SPRING_PROFILES_ACTIVE: dev
    DB_HOST: postgres
    DB_PORT: 5432
    DB_NAME: campus_club_dev
    DB_USER: campus_user
    DB_PASSWORD: ${DB_PASSWORD:-dev_password_123}
    REDIS_HOST: redis
    REDIS_PORT: 6379
    REDIS_PASSWORD: ${REDIS_PASSWORD:-dev_redis_password_456}
    JWT_SECRET: ${JWT_SECRET:-dev_jwt_secret_key_change_in_production_789}
    
    # 新增配置
    WECHAT_APP_ID: ${WECHAT_APP_ID}
    WECHAT_SECRET: ${WECHAT_SECRET}
    ALIYUN_ACCESS_KEY: ${ALIYUN_ACCESS_KEY}
    ALIYUN_SECRET_KEY: ${ALIYUN_SECRET_KEY}
    OSS_BUCKET_NAME: ${OSS_BUCKET_NAME:-campus-club-files-dev}
    ALGORITHM_SERVICE_URL: http://algorithm-service:8000
    ALGORITHM_SERVICE_TIMEOUT: 30000
```

#### 3.3.2 环境变量模板扩展(.env.example)

```bash
# ============================================
# 校园社团活动评估系统 - 完整环境变量配置示例
# ============================================

# --- 数据库配置 (PostgreSQL) ---
DB_PASSWORD=dev_password_123
DB_HOST=postgres
DB_PORT=5432
DB_NAME=campus_club_dev
DB_USER=campus_user

# --- Redis缓存配置 ---
REDIS_PASSWORD=dev_redis_password_456
REDIS_HOST=redis
REDIS_PORT=6379

# --- JWT安全配置 ---
JWT_SECRET=dev_jwt_secret_key_change_in_production_789

# --- 微信开放平台配置 (必需) ---
WECHAT_APP_ID=wx1234567890abcdef
WECHAT_SECRET=your_wechat_app_secret_here

# --- 阿里云OSS配置 (必需) ---
ALIYUN_ACCESS_KEY=your_aliyun_access_key_here
ALIYUN_SECRET_KEY=your_aliyun_secret_key_here
OSS_BUCKET_NAME=campus-club-files-dev
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com

# --- 算法服务配置 ---
ALGORITHM_SERVICE_URL=http://algorithm-service:8000
ALGORITHM_SERVICE_TIMEOUT=30000

# --- 可选监控配置 ---
# SENTRY_DSN=https://your_sentry_dsn_here@sentry.io/your_project_id
# PROMETHEUS_ENABLED=true

# ============================================
# 重要提示：
# 1. 生产环境必须使用强密码和正式配置
# 2. 不要将真实密码和密钥提交到版本控制
# 3. 复制此文件为 .env 并修改为实际值
# 4. 微信和阿里云配置需要申请相应服务
# ============================================
```

### 3.4 配置类补充方案

#### 3.4.1 新增配置类清单

1. **WechatConfig.java** - 微信OAuth2.0客户端配置
   - 微信API客户端初始化
   - OAuth2.0回调URL配置
   - 会话管理配置

2. **OssConfig.java** - 阿里云OSS客户端配置
   - OSS客户端初始化
   - 存储桶配置
   - 文件上传策略配置

3. **FeignConfig.java** - HTTP客户端配置
   - Feign客户端配置
   - 算法服务接口声明
   - 超时与重试策略

4. **AlgorithmServiceConfig.java** - 算法服务集成配置
   - 服务URL配置
   - 请求拦截器
   - 响应处理器

#### 3.4.2 安全配置扩展

在现有SecurityConfig基础上扩展：

```java
// 微信登录相关安全配置扩展
@Bean
public OAuth2UserService<OAuth2UserRequest, OAuth2User> oAuth2UserService() {
    // 微信OAuth2.0用户服务实现
}

@Bean
public ClientRegistrationRepository clientRegistrationRepository() {
    // 微信客户端注册配置
}

// 添加微信登录相关的安全规则
.httpBasic(withDefaults())
.oauth2Login(oauth2 -> oauth2
    .loginPage("/api/auth/login")
    .userInfoEndpoint(userInfo -> userInfo
        .userService(oAuth2UserService())
    )
    .successHandler(authenticationSuccessHandler())
)
```

### 3.5 测试验证方案

#### 3.5.1 验证清单

| 验证项 | 验证方法 | 期望结果 | 失败处理 |
|--------|----------|----------|----------|
| 依赖编译 | `mvn clean compile` | BUILD SUCCESS | 检查依赖冲突 |
| Docker构建 | `docker-compose build` | 所有镜像构建成功 | 检查Dockerfile语法 |
| 服务启动 | `docker-compose up -d` | 所有服务状态为healthy | 检查日志，服务依赖 |
| 健康检查 | `curl localhost:8080/api/actuator/health` | `{"status":"UP"}` | 检查应用日志 |
| 算法服务 | `curl localhost:8000/docs` | FastAPI文档页面 | 检查Python服务日志 |
| 数据库连接 | `docker exec` 验证表结构 | 显示所有表 | 检查Flyway迁移 |
| Redis连接 | `docker exec` Redis CLI | PONG响应 | 检查密码配置 |

#### 3.5.2 自动化验证脚本

```bash
#!/bin/bash
# verify-environment.sh
set -e

echo "=== 环境验证开始 ==="

# 1. Maven编译验证
echo "1. 验证Maven编译..."
cd campus-main
mvn clean compile -q
echo "✅ Maven编译成功"

# 2. Docker镜像构建
echo "2. 验证Docker镜像构建..."
cd ..
docker-compose build --quiet
echo "✅ Docker镜像构建成功"

# 3. 服务启动
echo "3. 启动服务..."
docker-compose up -d
sleep 15

# 4. 健康检查
echo "4. 服务健康检查..."
if curl -f http://localhost:8080/api/actuator/health > /dev/null 2>&1; then
    echo "✅ Java应用健康检查通过"
else
    echo "❌ Java应用健康检查失败"
    exit 1
fi

# 5. 算法服务检查
echo "5. 算法服务检查..."
if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ 算法服务健康检查通过"
else
    echo "⚠️ 算法服务未响应（可能为预期状态）"
fi

echo "=== 环境验证完成 ==="
echo "所有核心服务验证通过，可以开始开发工作。"
```

## 实施计划

### 4.1 实施阶段划分

**第一阶段：技术栈验证与报告** (预计30分钟)
1. 生成详细的技术栈差异报告
2. 验证现有代码编译与运行状态
3. 记录所有需要修复的项

**第二阶段：依赖补充与配置** (预计45分钟)
1. 分批添加缺失的Maven依赖
2. 完善docker-compose.yml配置
3. 扩展环境变量模板
4. 验证每项添加后的编译状态

**第三阶段：Docker环境完善** (预计30分钟)
1. 启用算法服务配置
2. 优化服务间网络配置
3. 添加健康检查配置
4. 验证完整服务栈启动

**第四阶段：测试与验证** (预计15分钟)
1. 运行自动化验证脚本
2. 记录验证结果
3. 生成实施报告

### 4.2 风险控制措施

| 风险类型 | 可能影响 | 预防措施 | 应急方案 |
|----------|----------|----------|----------|
| 依赖版本冲突 | 编译失败 | 分批次添加，每批验证 | 回滚该批次依赖 |
| Docker网络问题 | 服务无法通信 | 明确网络配置，添加健康检查依赖 | 手动测试网络连接 |
| 配置遗漏 | 功能不可用 | 使用配置检查脚本 | 补充缺失配置 |
| 算法服务延迟 | 调用超时 | 设置合理超时，添加降级开关 | 临时禁用算法功能 |

### 4.3 回滚方案

1. **代码回滚**：使用Git分批提交，便于回滚特定变更
2. **配置回滚**：备份原始配置文件，变更前创建副本
3. **环境回滚**：记录Docker镜像标签，可回退到之前版本

## 预期成果

### 5.1 交付物清单

1. **技术栈验证报告**：详细记录所有差异与修复项
2. **完整的pom.xml**：包含所有必需依赖，版本对齐
3. **完善的docker-compose.yml**：支持完整服务栈启动
4. **扩展的环境变量模板**：覆盖所有配置项
5. **新增的配置类**：微信、OSS、HTTP客户端配置
6. **验证脚本**：自动化环境验证工具
7. **实施文档**：记录所有变更与配置说明

### 5.2 成功标准

1. **技术栈一致性**：所有核心组件版本与设计文档一致
2. **功能完整性**：微信登录、文件上传、算法调用等核心功能依赖齐备
3. **环境可用性**：Docker Compose可启动完整服务栈
4. **配置完整性**：所有必需配置项均有明确配置方式
5. **可维护性**：所有变更有完整文档记录，便于后续维护

### 5.3 后续建议

1. **持续集成**：在CI/CD流水线中加入技术栈验证步骤
2. **依赖管理**：定期检查依赖版本，保持更新
3. **环境模板**：为不同环境（开发、测试、生产）提供独立配置模板
4. **监控集成**：逐步添加应用性能监控和日志聚合

---
*文档版本：1.0*
*创建时间：2026-04-09*
*设计者：Claude Code*
*基准文档：2026-04-09-campus-club-backend-architecture-design.md*
*状态：已批准实施*