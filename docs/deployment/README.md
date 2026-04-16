# 部署运维文档

本文档介绍校园社团系统的部署和运维操作。

---

## 目录

1. [环境要求](#环境要求)
2. [本地开发环境](#本地开发环境)
3. [生产环境部署](#生产环境部署)
4. [Docker 部署](#docker-部署)
5. [监控告警](#监控告警)
6. [运维操作](#运维操作)

---

## 环境要求

### 服务器配置

| 服务 | 最低配置 | 推荐配置 |
|------|----------|----------|
| Java后端 | 2核4G | 4核8G |
| Python算法 | 4核8G | 8核16G |
| PostgreSQL | 2核4G | 4核8G |
| Redis | 1核2G | 2核4G |
| 前端(Nginx) | 1核1G | 2核2G |

### 软件版本

| 软件 | 版本 |
|------|------|
| Java | 21+ |
| Python | 3.10+ |
| Node.js | 18+ |
| PostgreSQL | 14+ |
| Redis | 6+ |
| Nginx | 1.20+ |
| Docker | 24+ |

---

## 本地开发环境

### 1. 启动 PostgreSQL

```bash
# Docker 方式
docker run -d \
  --name campus-postgres \
  -e POSTGRES_DB=campus_db \
  -e POSTGRES_USER=campus \
  -e POSTGRES_PASSWORD=campus123 \
  -p 5432:5432 \
  postgres:14

# 或者使用本地 PostgreSQL
# 创建数据库和用户
psql -U postgres
cREATE DATABASE campus_db;
CREATE USER campus WITH PASSWORD 'campus123';
GRANT ALL PRIVILEGES ON DATABASE campus_db TO campus;
```

### 2. 启动 Redis

```bash
# Docker 方式
docker run -d \
  --name campus-redis \
  -p 6379:6379 \
  redis:6-alpine

# 带密码的 Redis
docker run -d \
  --name campus-redis \
  -p 6379:6379 \
  redis:6-alpine \
  redis-server --requirepass campus123
```

### 3. 配置 hosts (可选)

```bash
# 编辑 /etc/hosts 或 C:\Windows\System32\drivers\etc\hosts
127.0.0.1  campus.local
127.0.0.1  api.campus.local
127.0.0.1  ai.campus.local
```

---

## 生产环境部署

### 目录结构

```
/opt/campus-system/
├── campus-main/          # Java后端
├── campus-ai/            # Python算法
├── campus-frontend/      # 前端构建产物
├── nginx/                # Nginx配置
├── logs/                 # 日志目录
└── scripts/              # 运维脚本
```

### Java 后端部署

#### 1. 配置文件

创建 `application-prod.yml`:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/campus_db
    username: ${DB_USERNAME:campus}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000

  redis:
    host: localhost
    port: 6379
    password: ${REDIS_PASSWORD}
    lettuce:
      pool:
        max-active: 20
        max-idle: 10

  jpa:
    hibernate:
      ddl-auto: validate  # 生产环境使用 validate
    show-sql: false

server:
  port: 8080
  compression:
    enabled: true

logging:
  level:
    root: INFO
    com.campusclub: INFO
  file:
    name: /opt/campus-system/logs/campus-main/app.log

# 算法服务配置
algorithm:
  service:
    url: http://localhost:8000
    timeout: 30000
```

#### 2. 打包部署

```bash
cd campus-main

# 打包
mvn clean package -DskipTests -P prod

# 部署
scp target/campus-main-*.jar user@server:/opt/campus-system/campus-main/

# 启动 (服务器上)
cd /opt/campus-system/campus-main
nohup java -jar \
  -Xms2g -Xmx4g \
  -XX:+UseG1GC \
  -Dspring.profiles.active=prod \
  -Dlogging.file.name=/opt/campus-system/logs/campus-main/app.log \
  campus-main-*.jar > /dev/null 2>&1 &
```

#### 3. Systemd 服务

创建 `/etc/systemd/system/campus-main.service`:

```ini
[Unit]
Description=Campus Main Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=campus
WorkingDirectory=/opt/campus-system/campus-main
Environment="DB_PASSWORD=your_secure_password"
Environment="REDIS_PASSWORD=your_secure_password"
Environment="SPRING_PROFILES_ACTIVE=prod"
ExecStart=/usr/bin/java -Xms2g -Xmx4g -XX:+UseG1GC -jar campus-main-*.jar
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable campus-main
sudo systemctl start campus-main
sudo systemctl status campus-main
```

### Python 算法服务部署

#### 1. 环境配置

```bash
cd /opt/campus-system/campus-ai

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件
cat > .env << EOF
ENVIRONMENT=production
DATABASE_URL=postgresql://campus:password@localhost:5432/campus_db
REDIS_URL=redis://:password@localhost:6379/0
LOG_LEVEL=INFO
MAX_WORKERS=4
EOF
```

#### 2. 使用 Gunicorn 启动

```bash
# 安装 gunicorn
pip install gunicorn

# 启动 (测试)
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile /opt/campus-system/logs/campus-ai/access.log \
  --error-logfile /opt/campus-system/logs/campus-ai/error.log
```

#### 3. Systemd 服务

创建 `/etc/systemd/system/campus-ai.service`:

```ini
[Unit]
Description=Campus AI Service
After=network.target

[Service]
Type=simple
User=campus
WorkingDirectory=/opt/campus-system/campus-ai
Environment="PATH=/opt/campus-system/campus-ai/venv/bin"
Environment="PYTHONPATH=/opt/campus-system/campus-ai"
ExecStart=/opt/campus-system/campus-ai/venv/bin/gunicorn \
    src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /opt/campus-system/logs/campus-ai/access.log \
    --error-logfile /opt/campus-system/logs/campus-ai/error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 前端部署

#### 1. 构建

```bash
cd campus-frontend

# 安装依赖
pnpm install

# 构建社团端
pnpm build:club

# 构建管理端
pnpm build:admin

# 构建学生端 (微信小程序)
pnpm build:student
```

#### 2. Nginx 配置

```nginx
# /etc/nginx/conf.d/campus.conf

upstream campus_backend {
    server localhost:8080;
    keepalive 32;
}

upstream campus_ai {
    server localhost:8000;
    keepalive 32;
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name campus.local;
    return 301 https://$server_name$request_uri;
}

# 社团端
server {
    listen 443 ssl http2;
    server_name club.campus.local;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    root /opt/campus-system/campus-frontend/packages/club/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://campus_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Connection "";
        proxy_http_version 1.1;
    }
}

# 管理端
server {
    listen 443 ssl http2;
    server_name admin.campus.local;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    root /opt/campus-system/campus-frontend/packages/admin/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://campus_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# API 和 AI 服务 (内部)
server {
    listen 443 ssl http2;
    server_name api.campus.local;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://campus_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Docker 部署

### Docker Compose 配置

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: campus_db
      POSTGRES_USER: campus
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U campus"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  campus-main:
    build:
      context: ./campus-main
      dockerfile: Dockerfile
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs/campus-main:/app/logs

  campus-ai:
    build:
      context: ./campus-ai
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://campus:${DB_PASSWORD}@postgres:5432/campus_db
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs/campus-ai:/app/logs
      - ./models_cache:/app/models_cache

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./campus-frontend/packages/club/dist:/usr/share/nginx/html/club
      - ./campus-frontend/packages/admin/dist:/usr/share/nginx/html/admin
    depends_on:
      - campus-main
      - campus-ai

volumes:
  postgres_data:
  redis_data:
```

启动:
```bash
# 创建环境变量文件
cat > .env << EOF
DB_PASSWORD=your_secure_password
REDIS_PASSWORD=your_secure_password
EOF

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 监控告警

### 日志收集

使用 ELK 或 Loki 收集日志:

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log:ro
      - ./logs:/opt/campus-system/logs:ro
      - ./promtail-config.yaml:/etc/promtail/config.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### 健康检查端点

| 服务 | 健康检查端点 |
|------|--------------|
| Java后端 | GET http://localhost:8080/actuator/health |
| Python算法 | GET http://localhost:8000/health |
| PostgreSQL | pg_isready |
| Redis | redis-cli ping |

### 关键指标监控

```yaml
# 告警规则示例
groups:
  - name: campus_alerts
    rules:
      - alert: CampusMainDown
        expr: up{job="campus-main"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Java后端服务不可用"

      - alert: CampusAIDown
        expr: up{job="campus-ai"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Python算法服务不可用"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "错误率超过5%"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95响应时间超过2秒"
```

---

## 运维操作

### 日常检查清单

```bash
#!/bin/bash
# /opt/campus-system/scripts/daily-check.sh

echo "=== 每日系统检查 ==="
echo "检查时间: $(date)"

# 检查服务状态
echo -e "\n[服务状态]"
systemctl is-active campus-main && echo "✓ Java后端运行正常" || echo "✗ Java后端异常"
systemctl is-active campus-ai && echo "✓ Python算法运行正常" || echo "✗ Python算法异常"
systemctl is-active nginx && echo "✓ Nginx运行正常" || echo "✗ Nginx异常"

# 检查磁盘空间
echo -e "\n[磁盘空间]"
df -h | grep -E "(Filesystem|/dev/)"

# 检查内存使用
echo -e "\n[内存使用]"
free -h

# 检查日志错误
echo -e "\n[最近错误]"
journalctl -u campus-main --since "1 hour ago" | grep -i error | tail -5

# 检查数据库连接
echo -e "\n[数据库连接]"
psql -U campus -d campus_db -c "SELECT count(*) FROM pg_stat_activity;"

echo -e "\n=== 检查完成 ==="
```

### 备份策略

```bash
#!/bin/bash
# /opt/campus-system/scripts/backup.sh

BACKUP_DIR="/opt/backups/campus-system"
DATE=$(date +%Y%m%d_%H%M%S)

# 数据库备份
echo "备份数据库..."
pg_dump -U campus -d campus_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# 保留最近7天备份
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

# 日志备份
echo "备份日志..."
tar czf "$BACKUP_DIR/logs_$DATE.tar.gz" /opt/campus-system/logs/

# 文件备份 (OSS同步)
echo "同步文件到OSS..."
ossutil cp -r /opt/campus-system/uploads/ oss://campus-bucket/uploads/

echo "备份完成: $DATE"
```

### 故障排查

#### Java后端无法启动

```bash
# 1. 检查日志
journalctl -u campus-main -f

# 2. 检查端口占用
netstat -tlnp | grep 8080

# 3. 检查数据库连接
psql -U campus -h localhost -d campus_db -c "SELECT 1"

# 4. 检查配置文件
java -jar campus-main-*.jar --debug
```

#### Python算法服务无响应

```bash
# 1. 检查GPU状态 (如使用GPU)
nvidia-smi

# 2. 检查内存使用
free -h

# 3. 重启服务
systemctl restart campus-ai

# 4. 查看详细日志
tail -f /opt/campus-system/logs/campus-ai/error.log
```

#### 数据库性能问题

```sql
-- 查看慢查询
SELECT * FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;

-- 查看锁等待
SELECT * FROM pg_locks WHERE NOT granted;

-- 查看连接数
SELECT count(*), state FROM pg_stat_activity 
GROUP BY state;
```

### 性能优化

#### Java后端优化

```bash
# JVM参数优化
java -jar \
  -Xms4g -Xmx4g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:+ParallelRefProcEnabled \
  -XX:ParallelGCThreads=4 \
  -XX:ConcGCThreads=2 \
  campus-main-*.jar
```

#### PostgreSQL优化

```sql
-- postgresql.conf 优化
max_connections = 200
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
work_mem = 10MB
random_page_cost = 1.1
effective_io_concurrency = 200
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
```

---

## 变更日志

### 2024-04-15
- 新增 Docker Compose 部署方案
- 新增 Systemd 服务配置
- 完善监控告警配置
