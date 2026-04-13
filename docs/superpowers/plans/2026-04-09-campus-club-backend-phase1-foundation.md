# 校园社团活动评估系统 - 第一阶段：基础框架搭建实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立校园社团活动评估系统的后端基础框架，包括Spring Boot项目初始化、基础依赖配置、Docker环境配置和数据库表结构创建。

**Architecture:** 采用Spring Boot 3.2.x + Java 17技术栈，PostgreSQL 15.x作为主数据库，Redis 7.2.x作为缓存层。项目采用模块化设计，为后续业务模块开发奠定基础。

**Tech Stack:** Java 17, Spring Boot 3.2.x, Spring Security, Spring Data JPA, PostgreSQL 15.x, Redis 7.2.x, Docker, Docker Compose, Maven 3.9+

---

## 文件结构

```
campus-club-backend/
├── campus-main/                    # Java核心业务应用
│   ├── src/main/java/com/campusclub/
│   │   ├── CampusClubApplication.java  # 主启动类
│   │   ├── config/                    # 配置类目录
│   │   │   ├── SecurityConfig.java    # 安全配置
│   │   │   ├── JpaConfig.java         # JPA配置
│   │   │   ├── RedisConfig.java       # Redis配置
│   │   │   └── WebConfig.java         # Web配置
│   │   ├── common/                    # 公共模块
│   │   │   ├── exception/             # 异常处理
│   │   │   ├── model/                 # 公共模型
│   │   │   └── util/                  # 工具类
│   │   └── db/                        # 数据库相关
│   │       ├── migration/             # 数据库迁移脚本
│   │       └── repository/            # 基础Repository
│   ├── src/main/resources/
│   │   ├── application.yml            # 主配置文件
│   │   ├── application-dev.yml        # 开发环境配置
│   │   ├── application-prod.yml       # 生产环境配置
│   │   └── db/migration/              # Flyway迁移脚本
│   ├── Dockerfile                     # Java应用Dockerfile
│   └── pom.xml                        # Maven依赖管理
├── campus-ai/                        # Python算法服务（第一阶段占位）
│   ├── Dockerfile                    # Python服务Dockerfile
│   └── requirements.txt              # Python依赖（占位）
├── docker-compose.yml                # 容器编排文件
├── .env.example                      # 环境变量示例文件
├── README.md                         # 项目说明文档
└── .gitignore                        # Git忽略文件
```

---

## 任务分解

### Task 1: Spring Boot项目初始化

**Files:**
- Create: `campus-main/pom.xml`
- Create: `campus-main/src/main/java/com/campusclub/CampusClubApplication.java`
- Create: `campus-main/src/main/resources/application.yml`

- [ ] **Step 1: 创建Maven项目结构**

```bash
mkdir -p campus-main/src/main/java/com/campusclub
mkdir -p campus-main/src/main/resources/db/migration
mkdir -p campus-main/src/test/java/com/campusclub
```

- [ ] **Step 2: 创建pom.xml依赖文件**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.5</version>
        <relativePath/>
    </parent>

    <groupId>com.campusclub</groupId>
    <artifactId>campus-club-backend</artifactId>
    <version>1.0.0</version>
    <name>campus-club-backend</name>
    <description>校园社团活动评估系统后端</description>

    <properties>
        <java.version>17</java.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <mapstruct.version>1.5.5.Final</mapstruct.version>
        <lombok.version>1.18.30</lombok.version>
    </properties>

    <dependencies>
        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>

        <!-- Database -->
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
        </dependency>

        <!-- Utilities -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>${lombok.version}</version>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.mapstruct</groupId>
            <artifactId>mapstruct</artifactId>
            <version>${mapstruct.version}</version>
        </dependency>
        <dependency>
            <groupId>org.mapstruct</groupId>
            <artifactId>mapstruct-processor</artifactId>
            <version>${mapstruct.version}</version>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-jsr310</artifactId>
        </dependency>

        <!-- JWT -->
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-api</artifactId>
            <version>0.12.3</version>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-impl</artifactId>
            <version>0.12.3</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-jackson</artifactId>
            <version>0.12.3</version>
            <scope>runtime</scope>
        </dependency>

        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.security</groupId>
            <artifactId>spring-security-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>${java.version}</source>
                    <target>${java.version}</target>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                            <version>${lombok.version}</version>
                        </path>
                        <path>
                            <groupId>org.mapstruct</groupId>
                            <artifactId>mapstruct-processor</artifactId>
                            <version>${mapstruct.version}</version>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

- [ ] **Step 3: 创建Spring Boot主启动类**

```java
package com.campusclub;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@SpringBootApplication
@EnableJpaAuditing
public class CampusClubApplication {
    public static void main(String[] args) {
        SpringApplication.run(CampusClubApplication.class, args);
    }
}
```

- [ ] **Step 4: 创建基础配置文件**

```yaml
# application.yml
spring:
  application:
    name: campus-club-backend

  profiles:
    active: dev

  jackson:
    time-zone: Asia/Shanghai
    date-format: yyyy-MM-dd HH:mm:ss
    serialization:
      write-dates-as-timestamps: false

server:
  port: 8080
  servlet:
    context-path: /api
    encoding:
      charset: UTF-8
      enabled: true
      force: true

logging:
  level:
    com.campusclub: DEBUG
    org.springframework.security: INFO
    org.hibernate.SQL: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: logs/app.log
    max-size: 10MB
    max-history: 30

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
```

- [ ] **Step 5: 测试项目能否编译**

```bash
cd campus-main
mvn clean compile
```

期望输出: `BUILD SUCCESS`

- [ ] **Step 6: 提交初始代码**

```bash
git add campus-main/pom.xml campus-main/src/main/java/com/campusclub/CampusClubApplication.java campus-main/src/main/resources/application.yml
git commit -m "feat: initialize Spring Boot project structure"
```

---

### Task 2: 基础依赖配置

**Files:**
- Create: `campus-main/src/main/java/com/campusclub/config/SecurityConfig.java`
- Create: `campus-main/src/main/java/com/campusclub/config/JpaConfig.java`
- Create: `campus-main/src/main/java/com/campusclub/config/RedisConfig.java`
- Create: `campus-main/src/main/java/com/campusclub/config/WebConfig.java`
- Create: `campus-main/src/main/resources/application-dev.yml`
- Create: `campus-main/src/main/resources/application-prod.yml`

- [ ] **Step 1: 创建开发环境配置文件**

```yaml
# application-dev.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/campus_club_dev
    username: campus_user
    password: dev_password_123
    driver-class-name: org.postgresql.Driver
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000

  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
        jdbc:
          batch_size: 20
        order_inserts: true
        order_updates: true
    show-sql: true

  data:
    redis:
      host: localhost
      port: 6379
      password: dev_redis_password_456
      timeout: 5000ms
      lettuce:
        pool:
          max-active: 8
          max-idle: 8
          min-idle: 0
          max-wait: -1ms

  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration

jwt:
  secret: dev_jwt_secret_key_change_in_production_789
  expiration: 7200000 # 2小时
  refresh-expiration: 604800000 # 7天
```

- [ ] **Step 2: 创建生产环境配置文件**

```yaml
# application-prod.yml
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST:postgres}:${DB_PORT:5432}/${DB_NAME:campus_club}
    username: ${DB_USER:campus_user}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 10
      connection-timeout: 30000

  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false

  data:
    redis:
      host: ${REDIS_HOST:redis}
      port: ${REDIS_PORT:6379}
      password: ${REDIS_PASSWORD}
      timeout: 10000ms

  flyway:
    enabled: true
    validate-on-migrate: true

jwt:
  secret: ${JWT_SECRET}
  expiration: 7200000
  refresh-expiration: 604800000

logging:
  level:
    com.campusclub: INFO
    org.springframework.security: WARN
```

- [ ] **Step 3: 创建安全配置类**

```java
package com.campusclub.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                // 公开访问的接口
                .requestMatchers(
                    "/api/auth/**",
                    "/api/public/**",
                    "/actuator/health",
                    "/v3/api-docs/**",
                    "/swagger-ui/**",
                    "/swagger-ui.html"
                ).permitAll()
                // 需要认证的接口
                .anyRequest().authenticated()
            );
        
        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(List.of("http://localhost:3000", "http://localhost:5173"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

- [ ] **Step 4: 创建JPA配置类**

```java
package com.campusclub.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableJpaAuditing
@EnableTransactionManagement
@EnableJpaRepositories(basePackages = "com.campusclub.**.repository")
public class JpaConfig {
    // JPA配置已通过注解完成
}
```

- [ ] **Step 5: 创建Redis配置类**

```java
package com.campusclub.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        
        // 使用String序列化key
        template.setKeySerializer(new StringRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        
        // 使用Jackson序列化value
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        
        template.afterPropertiesSet();
        return template;
    }
}
```

- [ ] **Step 6: 创建Web配置类**

```java
package com.campusclub.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {
    // 目前为空，后续可添加拦截器、格式化器等配置
}
```

- [ ] **Step 7: 测试配置类编译**

```bash
cd campus-main
mvn clean compile
```

期望输出: `BUILD SUCCESS`

- [ ] **Step 8: 提交配置代码**

```bash
git add campus-main/src/main/java/com/campusclub/config/ campus-main/src/main/resources/application-*.yml
git commit -m "feat: add configuration classes and environment configs"
```

---

### Task 3: Docker环境配置

**Files:**
- Create: `campus-main/Dockerfile`
- Create: `campus-ai/Dockerfile` (占位符)
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `.gitignore`

- [ ] **Step 1: 创建Java应用Dockerfile**

```dockerfile
# campus-main/Dockerfile
# 构建阶段
FROM eclipse-temurin:17-jdk-alpine AS builder
WORKDIR /app

# 复制Maven配置和源代码
COPY pom.xml .
COPY src ./src

# 下载依赖并构建
RUN apk add --no-cache maven \
    && mvn clean package -DskipTests

# 运行阶段
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# 安装必要的工具
RUN apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone

# 创建非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 从构建阶段复制jar文件
COPY --from=builder /app/target/*.jar app.jar

# 设置权限
RUN chown -R appuser:appgroup /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/actuator/health || exit 1

# 启动命令
ENTRYPOINT ["java", "-jar", "app.jar"]
```

- [ ] **Step 2: 创建Python算法服务Dockerfile（占位符）**

```dockerfile
# campus-ai/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src/

# 暴露端口
EXPOSE 8000

# 启动命令（将在后续阶段实现）
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: 创建requirements.txt（占位符）**

```txt
# campus-ai/requirements.txt
# Python算法服务依赖（将在后续阶段完善）
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
```

- [ ] **Step 4: 创建Docker Compose编排文件**

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: campus-postgres
    environment:
      POSTGRES_DB: campus_club_dev
      POSTGRES_USER: campus_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-dev_password_123}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U campus_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - campus-network

  redis:
    image: redis:7-alpine
    container_name: campus-redis
    command: redis-server --requirepass ${REDIS_PASSWORD:-dev_redis_password_456}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - campus-network

  java-app:
    build:
      context: ./campus-main
      dockerfile: Dockerfile
    container_name: campus-java
    environment:
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
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./campus-main/src:/app/src:ro
    networks:
      - campus-network

  # Python算法服务（将在后续阶段启用）
  # algorithm-service:
  #   build:
  #     context: ./campus-ai
  #     dockerfile: Dockerfile
  #   container_name: campus-algorithm
  #   environment:
  #     PYTHONPATH: /app
  #   ports:
  #     - "8000:8000"
  #   volumes:
  #     - ./campus-ai/src:/app/src:ro
  #   networks:
  #     - campus-network

volumes:
  postgres_data:
  redis_data:

networks:
  campus-network:
    driver: bridge
```

- [ ] **Step 5: 创建环境变量示例文件**

```bash
# .env.example
# ============================================
# 开发环境配置示例
# ============================================

# 数据库配置（PostgreSQL）
DB_PASSWORD=dev_password_123
DB_HOST=postgres
DB_PORT=5432
DB_NAME=campus_club_dev
DB_USER=campus_user

# Redis配置
REDIS_PASSWORD=dev_redis_password_456
REDIS_HOST=redis
REDIS_PORT=6379

# JWT配置
JWT_SECRET=dev_jwt_secret_key_change_in_production_789

# 重要提示：
# 1. 生产环境请使用强密码
# 2. 不要将真实密码提交到版本控制
# 3. 复制此文件为 .env 并修改为实际值
```

- [ ] **Step 6: 创建Git忽略文件**

```gitignore
# .gitignore
# Java
*.class
*.jar
*.war
*.ear
*.nar
*.zip
*.tar.gz
*.rar

# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup
pom.xml.next
release.properties
dependency-reduced-pom.xml
buildNumber.properties
.mvn/tmp.properties

# IDE
.idea/
*.iml
*.ipr
*.iws
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
.env
!/.env.example

# Logs
logs/
*.log

# Database
*.db
*.sqlite
*.h2.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Test
coverage/
htmlcov/
.tox/
.pytest_cache/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# 临时文件
tmp/
temp/
*.tmp
*.temp
```

- [ ] **Step 7: 测试Docker构建**

```bash
# 复制环境变量示例
cp .env.example .env

# 构建Java应用镜像
cd campus-main
docker build -t campus-java:dev .
```

期望输出: `Successfully built` 和 `Successfully tagged campus-java:dev`

- [ ] **Step 8: 提交Docker配置**

```bash
git add campus-main/Dockerfile campus-ai/ docker-compose.yml .env.example .gitignore
git commit -m "feat: add Docker configuration and environment setup"
```

---

### Task 4: 数据库表结构创建

**Files:**
- Create: `campus-main/src/main/resources/db/migration/V1__create_base_tables.sql`
- Create: `campus-main/src/main/java/com/campusclub/common/model/BaseEntity.java`
- Create: `campus-main/src/main/java/com/campusclub/db/repository/BaseRepository.java`
- Create: `campus-main/src/main/java/com/campusclub/common/exception/GlobalExceptionHandler.java`

- [ ] **Step 1: 创建基础实体类**

```java
package com.campusclub.common.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Getter
@Setter
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted", nullable = false)
    private Boolean deleted = false;
}
```

- [ ] **Step 2: 创建基础Repository接口**

```java
package com.campusclub.db.repository;

import com.campusclub.common.model.BaseEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.NoRepositoryBean;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@NoRepositoryBean
public interface BaseRepository<T extends BaseEntity> extends JpaRepository<T, Long> {
    
    @Query("SELECT e FROM #{#entityName} e WHERE e.deleted = false AND e.id = :id")
    Optional<T> findActiveById(Long id);
    
    @Query("SELECT e FROM #{#entityName} e WHERE e.deleted = false")
    List<T> findAllActive();
    
    @Transactional
    @Modifying
    @Query("UPDATE #{#entityName} e SET e.deleted = true WHERE e.id = :id")
    void softDeleteById(Long id);
    
    @Query("SELECT COUNT(e) FROM #{#entityName} e WHERE e.deleted = false")
    long countActive();
}
```

- [ ] **Step 3: 创建数据库迁移脚本**

```sql
-- V1__create_base_tables.sql
-- 用户与角色表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    openid VARCHAR(100) UNIQUE,
    username VARCHAR(50) NOT NULL,
    avatar_url VARCHAR(255),
    email VARCHAR(100),
    phone VARCHAR(20),
    password_hash VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'STUDENT',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE user_roles (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id)
);

-- 社团表
CREATE TABLE clubs (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    logo_url VARCHAR(255),
    president_id BIGINT REFERENCES users(id),
    faculty_advisor VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 活动表
CREATE TABLE activities (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    activity_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location VARCHAR(200),
    capacity INT NOT NULL DEFAULT 0,
    current_participants INT NOT NULL DEFAULT 0,
    club_id BIGINT NOT NULL REFERENCES clubs(id),
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT check_activity_time CHECK (end_time > start_time)
);

-- 活动参与表
CREATE TABLE activity_participants (
    activity_id BIGINT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'REGISTERED',
    check_in_time TIMESTAMP,
    feedback_score INT,
    feedback_text TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (activity_id, user_id),
    CONSTRAINT check_feedback_score CHECK (feedback_score IS NULL OR (feedback_score >= 1 AND feedback_score <= 5))
);

-- 资源表
CREATE TABLE resources (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    capacity INT,
    unit VARCHAR(20),
    available_count INT NOT NULL DEFAULT 0,
    total_count INT NOT NULL DEFAULT 0,
    constraints JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 资源预约表
CREATE TABLE resource_reservations (
    id BIGSERIAL PRIMARY KEY,
    resource_id BIGINT NOT NULL REFERENCES resources(id),
    activity_id BIGINT NOT NULL REFERENCES activities(id),
    quantity INT NOT NULL DEFAULT 1,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'RESERVED',
    approved_by BIGINT REFERENCES users(id),
    approved_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT check_reservation_time CHECK (end_time > start_time)
);

-- 评估指标表
CREATE TABLE evaluation_metrics (
    activity_id BIGINT PRIMARY KEY REFERENCES activities(id),
    participation_score DECIMAL(5,2),
    educational_score DECIMAL(5,2),
    innovation_score DECIMAL(5,2),
    influence_score DECIMAL(5,2),
    sustainability_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 非结构化数据表
CREATE TABLE unstructured_data (
    id BIGSERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    activity_id BIGINT REFERENCES activities(id),
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 索引创建
CREATE INDEX idx_users_openid ON users(openid);
CREATE INDEX idx_users_role ON users(role, status);
CREATE INDEX idx_activities_club_status ON activities(club_id, status);
CREATE INDEX idx_activities_time ON activities(start_time, end_time);
CREATE INDEX idx_activity_participants_user ON activity_participants(user_id, status);
CREATE INDEX idx_resources_type_status ON resources(type, status);
CREATE INDEX idx_resource_reservations_time ON resource_reservations(start_time, end_time);
CREATE INDEX idx_evaluation_metrics_score ON evaluation_metrics(overall_score);
CREATE INDEX idx_unstructured_data_processed ON unstructured_data(processed, source_type);

-- 初始数据插入
INSERT INTO roles (name, description) VALUES 
    ('SUPER_ADMIN', '超级管理员，拥有所有权限'),
    ('DEPARTMENT_ADMIN', '院系管理员，负责院系内社团管理'),
    ('CLUB_ADMIN', '社团管理员，负责单个社团管理'),
    ('STUDENT', '普通学生用户');

-- 创建初始超级管理员用户（密码：admin123）
INSERT INTO users (username, email, password_hash, role, status) VALUES 
    ('admin', 'admin@campus.edu', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iK6TMn6cF.8LzVqVhRw6p6l.Q1O6', 'SUPER_ADMIN', 'ACTIVE');
```

- [ ] **Step 4: 创建全局异常处理器**

```java
package com.campusclub.common.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<ErrorResponse> handleBadCredentialsException(BadCredentialsException ex, WebRequest request) {
        log.error("Authentication failed: {}", ex.getMessage());
        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.UNAUTHORIZED.value())
                .error("Unauthorized")
                .message("用户名或密码错误")
                .path(request.getDescription(false))
                .build();
        return new ResponseEntity<>(error, HttpStatus.UNAUTHORIZED);
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> handleAccessDeniedException(AccessDeniedException ex, WebRequest request) {
        log.error("Access denied: {}", ex.getMessage());
        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.FORBIDDEN.value())
                .error("Forbidden")
                .message("没有访问权限")
                .path(request.getDescription(false))
                .build();
        return new ResponseEntity<>(error, HttpStatus.FORBIDDEN);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationExceptions(MethodArgumentNotValidException ex, WebRequest request) {
        log.error("Validation error: {}", ex.getMessage());
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach(error -> {
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.put(fieldName, errorMessage);
        });
        
        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.BAD_REQUEST.value())
                .error("Bad Request")
                .message("请求参数验证失败")
                .path(request.getDescription(false))
                .details(errors)
                .build();
        return new ResponseEntity<>(error, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGlobalException(Exception ex, WebRequest request) {
        log.error("Unexpected error: {}", ex.getMessage(), ex);
        ErrorResponse error = ErrorResponse.builder()
                .timestamp(LocalDateTime.now())
                .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
                .error("Internal Server Error")
                .message("服务器内部错误")
                .path(request.getDescription(false))
                .build();
        return new ResponseEntity<>(error, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```

- [ ] **Step 5: 创建错误响应类**

```java
package com.campusclub.common.exception;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.Map;

@Data
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ErrorResponse {
    private LocalDateTime timestamp;
    private int status;
    private String error;
    private String message;
    private String path;
    private Map<String, String> details;
}
```

- [ ] **Step 6: 测试数据库迁移**

```bash
# 启动Docker Compose服务
docker-compose up -d postgres redis

# 等待服务启动
sleep 10

# 运行Flyway迁移
cd campus-main
mvn flyway:migrate -Dflyway.configFiles=src/main/resources/application-dev.yml
```

期望输出: `Successfully applied 1 migration`

- [ ] **Step 7: 验证数据库表创建**

```bash
# 连接到PostgreSQL容器验证表结构
docker exec -it campus-postgres psql -U campus_user -d campus_club_dev -c "\dt"
```

期望输出: 显示创建的所有表（users, roles, clubs, activities等）

- [ ] **Step 8: 提交数据库相关代码**

```bash
git add campus-main/src/main/resources/db/migration/ campus-main/src/main/java/com/campusclub/common/ campus-main/src/main/java/com/campusclub/db/
git commit -m "feat: create database schema, base entities and exception handling"
```

---

### Task 5: 基础测试与验证

**Files:**
- Create: `campus-main/src/test/java/com/campusclub/CampusClubApplicationTests.java`
- Create: `campus-main/src/test/java/com/campusclub/config/SecurityConfigTest.java`
- Create: `campus-main/src/test/resources/application-test.yml`

- [ ] **Step 1: 创建测试配置文件**

```yaml
# application-test.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
    driver-class-name: org.h2.Driver
    username: sa
    password: 
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: false
  data:
    redis:
      host: localhost
      port: 6379
      lettuce:
        pool:
          max-active: 8
  flyway:
    enabled: false

logging:
  level:
    com.campusclub: INFO
    org.springframework: WARN
```

- [ ] **Step 2: 创建应用启动测试**

```java
package com.campusclub;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class CampusClubApplicationTests {

    @Test
    void contextLoads() {
        // 测试Spring上下文能否正常加载
    }
}
```

- [ ] **Step 3: 创建安全配置测试**

```java
package com.campusclub.config;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@ActiveProfiles("test")
class SecurityConfigTest {

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Test
    void testPasswordEncoder() {
        // 测试密码加密
        String rawPassword = "testPassword123";
        String encodedPassword = passwordEncoder.encode(rawPassword);
        
        assertNotNull(encodedPassword);
        assertNotEquals(rawPassword, encodedPassword);
        assertTrue(passwordEncoder.matches(rawPassword, encodedPassword));
        assertFalse(passwordEncoder.matches("wrongPassword", encodedPassword));
    }
}
```

- [ ] **Step 4: 运行测试**

```bash
cd campus-main
mvn clean test
```

期望输出: `Tests run: 2, Failures: 0, Errors: 0, Skipped: 0`

- [ ] **Step 5: 测试Docker Compose完整启动**

```bash
# 停止现有服务
docker-compose down

# 启动所有服务
docker-compose up -d

# 等待服务启动
sleep 15

# 检查服务状态
docker-compose ps
```

期望输出: 所有服务状态为 `Up (healthy)`

- [ ] **Step 6: 测试应用健康检查**

```bash
# 测试健康检查端点
curl -f http://localhost:8080/api/actuator/health
```

期望输出: `{"status":"UP"}` 或类似的JSON响应

- [ ] **Step 7: 提交测试代码**

```bash
git add campus-main/src/test/
git commit -m "test: add basic tests and health check verification"
```

---

## 计划自审

### 1. 规格覆盖检查
- [x] Spring Boot项目初始化 - Task 1完成
- [x] 基础依赖配置 - Task 2完成
- [x] Docker环境配置 - Task 3完成
- [x] 数据库表结构创建 - Task 4完成
- [x] 基础测试与验证 - Task 5完成

所有第一阶段规格要求均已覆盖。

### 2. 占位符扫描
- [x] 无TBD、TODO等占位符
- [x] 所有代码示例完整
- [x] 所有测试命令明确
- [x] 所有预期输出明确

### 3. 类型一致性检查
- [x] 所有类名、方法名、变量名一致
- [x] 数据库表名与设计文档一致
- [x] 配置文件键名一致
- [x] Docker Compose服务名一致

## 执行选项

**计划已完成并保存至 [docs/superpowers/plans/2026-04-09-campus-club-backend-phase1-foundation.md](docs/superpowers/plans/2026-04-09-campus-club-backend-phase1-foundation.md)。**

**两种执行选项：**

**1. 子代理驱动（推荐）** - 我为每个任务分派新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用executing-plans执行任务，设置检查点进行审查

**选择哪种方式？**

如果选择子代理驱动：
- **必需子技能**：使用superpowers:subagent-driven-development
- 每个任务使用新的子代理 + 两阶段审查

如果选择内联执行：
- **必需子技能**：使用superpowers:executing-plans
- 批量执行并设置检查点进行审查

---

*计划版本：1.0*
*创建时间：2026-04-09*
*创建者：Claude Code*
*状态：就绪执行*