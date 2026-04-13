# Campus AI - 校园社团智能算法服务

## 项目概述

Campus AI 是一个为校园社团管理系统提供智能算法服务的后端应用。它集成了多种机器学习算法，包括聚类分析、层次分析法(AHP)和自然语言处理模型，为社团管理提供数据驱动的决策支持。

## 主要功能

- **社团聚类分析**: 使用K-means算法对社团进行智能分类
- **社团评估**: 基于层次分析法(AHP)的社团综合评估模型
- **自然语言处理**: 文本分析和情感分析功能
- **模型管理**: 支持模型缓存、预热和版本管理
- **监控告警**: 完整的性能监控和告警系统

## 技术栈

- **后端框架**: FastAPI + Uvicorn
- **机器学习**: PyTorch, Scikit-learn, Transformers
- **数据处理**: Pandas, NumPy, SciPy
- **存储**: PostgreSQL, Redis, 阿里云OSS
- **监控**: Prometheus, Grafana
- **开发工具**: Black, Ruff, MyPy, Pytest

## 快速开始

### 环境要求

- Python 3.10+
- PostgreSQL 13+
- Redis 6+

### 安装步骤

1. 克隆项目
   ```bash
   git clone <repository-url>
   cd campus-ai
   ```

2. 创建虚拟环境
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   ```

4. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入实际配置
   ```

5. 启动服务
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker 启动

```bash
docker build -t campus-ai .
docker run -p 8000:8000 --env-file .env campus-ai
```

## 项目结构

```
campus-ai/
├── src/                    # 源代码目录
│   ├── api/               # API路由
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   ├── algorithms/        # 算法实现
│   └── main.py           # 应用入口
├── config/                # 配置文件
├── deploy/                # 部署配置
├── monitoring/            # 监控配置
│   └── dashboards/       # Grafana仪表板
├── models_cache/          # 模型缓存
│   ├── kmeans/           # K-means模型缓存
│   └── ahp/              # AHP模型缓存
├── logs/                  # 日志文件
├── tests/                 # 测试文件
├── requirements.txt       # 生产依赖
├── requirements-dev.txt   # 开发依赖
├── .env.example          # 环境变量示例
├── Dockerfile            # Docker配置
├── .dockerignore         # Docker忽略文件
└── pyproject.toml        # 项目配置
```

## API文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发指南

### 代码规范

- 使用Black进行代码格式化
- 使用Ruff进行代码检查
- 使用MyPy进行类型检查
- 提交前运行pre-commit钩子

### 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src tests/

# 运行特定测试文件
pytest tests/test_api.py
```

### 代码质量检查

```bash
# 代码格式化
black src/

# 代码检查
ruff check src/

# 类型检查
mypy src/
```

## 部署

### 生产环境部署

1. 配置生产环境变量
2. 构建Docker镜像
3. 使用Docker Compose或Kubernetes部署
4. 配置监控和告警

### 监控配置

- Prometheus: 指标收集
- Grafana: 数据可视化
- AlertManager: 告警管理

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者: [维护者姓名]
- 问题反馈: [GitHub Issues](<issues-url>)
- 文档更新: [GitHub Wiki](<wiki-url>)