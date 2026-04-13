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