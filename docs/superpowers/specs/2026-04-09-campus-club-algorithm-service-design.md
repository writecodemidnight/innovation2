# 校园社团算法服务 - 详细设计规格

**项目名称**: 基于大数据分析的校园社团活动效果评估与资源优化系统 - 算法服务  
**设计版本**: 1.0  
**设计日期**: 2026-04-09  
**状态**: 已批准（等待实现）

## 1. 设计概述

### 1.1 核心目标
为校园社团活动评估系统提供算法能力，通过机器学习和大数据分析实现：
- 个性化活动推荐（K-Means聚类）
- 多层次活动评估（AHP层次分析法）
- 资源需求预测（LSTM时间序列）
- 情感分析（NLP技术）
- 图像质量分析（计算机视觉）
- 资源优化分配（遗传算法）
- 关联规则挖掘（Apriori算法）

### 1.2 架构决策
经过用户确认，采用以下技术方案：
- **架构模式**: 单体算法服务（方案一，推荐）
- **存储方案**: 阿里云OSS对象存储
- **模型版本**: 时间戳版本控制
- **集成方式**: REST API（选项B）
- **数据契约**: 精确JSON格式定义

## 2. 技术架构

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                    Spring Boot 核心业务单体                   │
│                Java 17 + Spring Boot 3.2.x                   │
│   ┌─────────────────────────────────────────────┐           │
│   │ 提供REST API供算法服务调用                    │           │
│   │ • 用户/活动/资源数据访问                      │           │
│   │ • 实时数据同步                              │           │
│   └─────────────────────────────────────────────┘           │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API (JSON + JWT认证)
┌─────────────────────────▼───────────────────────────────────┐
│                 Python FastAPI 算法服务单体                  │
│              Python 3.10 + FastAPI 0.104+                   │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┐        │
│  │K-Means│  AHP  │ LSTM │ GA   │ NLP  │ CV   │Apriori│        │
│  └──────┴──────┴──────┴──────┴──────┴──────┴──────┘        │
└─────────────────────────┬───────────────────────────────────┘
                          │ 阿里云OSS + 模型存储
┌─────────────────────────▼───────────────────────────────────┐
│                   阿里云OSS对象存储                          │
│   • 训练模型存储 (model/)                                   │
│   • 临时数据处理 (temp/)                                   │
│   • 评估结果缓存 (cache/)                                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 项目结构
```
campus-ai/
├── src/
│   ├── main.py                      # FastAPI主应用
│   ├── core/                        # 核心模块
│   │   ├── config.py               # 配置管理
│   │   ├── lifespan.py             # 生命周期管理（新增）
│   │   ├── security.py             # 认证安全
│   │   ├── exceptions.py           # 异常处理
│   │   ├── monitoring.py           # 监控指标
│   │   └── dependencies.py         # 依赖注入
│   ├── api/                        # API路由层
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── recommend.py       # 推荐相关接口
│   │   │   ├── evaluation.py      # 评估相关接口
│   │   │   ├── nlp.py             # NLP相关接口
│   │   │   ├── prediction.py      # 预测相关接口
│   │   │   ├── optimization.py    # 优化相关接口
│   │   │   ├── mining.py          # 数据挖掘接口
│   │   │   └── cv.py              # 计算机视觉接口
│   │   └── health.py              # 健康检查接口
│   ├── services/                   # 业务服务层
│   │   ├── recommendation.py      # K-Means推荐服务
│   │   ├── evaluation.py          # AHP评估服务
│   │   ├── prediction.py          # LSTM预测服务
│   │   ├── optimization.py        # 遗传算法优化服务
│   │   ├── nlp.py                 # NLP情感分析服务
│   │   ├── computer_vision.py     # CV图像质量分析
│   │   ├── mining.py              # Apriori关联规则挖掘
│   │   └── model_manager.py       # 模型管理服务（增强）
│   ├── models/                    # 数据模型
│   │   ├── schemas.py            # Pydantic模式（完整定义）
│   │   ├── dto.py                # 数据传输对象
│   │   └── entities.py           # 数据库实体（如需）
│   ├── utils/                     # 工具模块
│   │   ├── data_processor.py     # 数据预处理（增强）
│   │   ├── oss_client.py         # 阿里云OSS客户端
│   │   ├── spring_client.py      # Spring Boot API客户端
│   │   ├── metrics.py            # 评估指标计算
│   │   └── logging_config.py     # 日志配置
│   └── tests/                     # 测试目录
│       ├── unit/
│       ├── integration/
│       └── conftest.py
├── models/                        # 训练模型存储目录
│   ├── kmeans/                    # K-Means模型
│   ├── lstm/                      # LSTM模型
│   ├── ahp/                       # AHP权重矩阵
│   └── README.md                  # 模型说明
├── docker-compose.yml             # 本地开发环境
├── Dockerfile                     # 生产环境镜像
├── requirements.txt               # Python依赖（完整清单）
├── .env.example                   # 环境变量示例
├── config/
│   ├── development.yml            # 开发配置
│   ├── production.yml             # 生产配置
│   └── test.yml                   # 测试配置
└── README.md                      # 项目文档
```

## 3. API接口设计

### 3.1 基础信息
- **服务URL**: `http://algorithm-service:8000/api/v1`
- **通信协议**: REST API (JSON格式)
- **超时设置**: 默认30秒
- **重试策略**: 指数退避，最多3次
- **认证方式**: JWT Token（从Spring Boot获取）

### 3.2 算法接口详细设计

#### 3.2.1 `/recommend/kmeans` - K-Means个性化推荐
**方法**: POST  
**用途**: 基于用户历史活动进行个性化推荐

**请求体**:
```json
{
  "user_id": "string | integer",
  "history_activities": [
    {
      "activity_id": "string | integer",
      "activity_type": "string",
      "participation_score": "number | null",
      "feedback_score": "number | null",
      "timestamp": "ISO 8601"
    }
  ],
  "top_n": "integer, default=5",
  "include_metadata": "boolean, default=false"
}
```

**响应体**:
```json
{
  "request_id": "string (UUID)",
  "recommended_activities": [
    {
      "activity_id": "string | integer",
      "similarity_score": "number (0-1)",
      "confidence": "number (0-1)",
      "recommendation_reason": "string",
      "activity_metadata": {
        "title": "string",
        "activity_type": "string",
        "start_time": "ISO 8601"
      }
    }
  ],
  "algorithm_version": "string (timestamp)",
  "processing_time_ms": "number"
}
```

#### 3.2.2 `/evaluation/ahp` - AHP层次分析法评估
**方法**: POST  
**用途**: 多维度活动质量评估

**请求体**:
```json
{
  "activity_id": "string | integer",
  "metrics_data": {
    "participation": {
      "actual_count": "integer",
      "expected_count": "integer",
      "check_in_rate": "number"
    },
    "educational": {
      "content_quality": "number (1-5)",
      "knowledge_gain": "number (1-5)"
    },
    "innovation": {
      "novelty_score": "number (1-5)",
      "creativity_rating": "number (1-5)"
    },
    "influence": {
      "social_media_shares": "integer",
      "word_of_mouth_count": "integer"
    },
    "sustainability": {
      "resource_efficiency": "number (0-1)",
      "repeatability": "number (0-1)"
    }
  },
  "weights": {
    "participation": "number (0-1, sum=1)",
    "educational": "number (0-1, sum=1)",
    "innovation": "number (0-1, sum=1)",
    "influence": "number (0-1, sum=1)",
    "sustainability": "number (0-1, sum=1)"
  }
}
```

**响应体**:
```json
{
  "request_id": "string (UUID)",
  "scores": {
    "participation_score": "number (0-100)",
    "educational_score": "number (0-100)",
    "innovation_score": "number (0-100)",
    "influence_score": "number (0-100)",
    "sustainability_score": "number (0-100)",
    "overall_score": "number (0-100)"
  },
  "radar_data": {
    "labels": ["参与度", "教育性", "创新性", "影响力", "可持续性"],
    "datasets": [
      {
        "label": "当前活动",
        "data": ["number", "number", "number", "number", "number"]
      },
      {
        "label": "同类活动平均",
        "data": ["number", "number", "number", "number", "number"]
      }
    ]
  },
  "weight_matrix_used": "object",
  "consistency_ratio": "number",
  "algorithm_version": "string (timestamp)"
}
```

#### 3.2.3 `/nlp/sentiment` - NLP情感分析
**方法**: POST  
**用途**: 分析用户反馈文本的情感倾向

**请求体**:
```json
{
  "texts": ["string"],
  "language": "string, default='zh-CN'",
  "return_probabilities": "boolean, default=false"
}
```

**响应体**:
```json
{
  "sentiments": [
    {
      "text": "string",
      "sentiment": "POSITIVE | NEUTRAL | NEGATIVE",
      "score": "number (0-1)",
      "probabilities": {
        "positive": "number",
        "neutral": "number", 
        "negative": "number"
      }
    }
  ],
  "language_detected": "string",
  "model_version": "string"
}
```

#### 3.2.4 `/prediction/lstm` - LSTM资源需求预测
**方法**: POST  
**用途**: 预测未来活动资源需求

#### 3.2.5 `/optimization/ga` - 遗传算法资源优化
**方法**: POST  
**用途**: 优化活动资源分配方案

#### 3.2.6 `/mining/apriori` - Apriori关联规则挖掘
**方法**: POST  
**用途**: 发现活动参与模式关联规则

#### 3.2.7 `/cv/quality` - 计算机视觉图像质量分析
**方法**: POST  
**用途**: 分析活动现场图片质量

## 4. 技术栈与依赖

### 4.1 Python依赖清单（requirements.txt）
```txt
# FastAPI框架
fastapi[all]==0.104.1  # 包含uvicorn、pydantic等
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# 阿里云集成
aliyun-python-sdk-oss==2.18.6
oss2==2.18.4
python-jose[cryptography]==3.3.0  # JWT处理

# HTTP客户端（用于调用Spring Boot API）
httpx==0.26.0
asyncio-throttle==1.0.2  # 限流保护

# 机器学习算法库
scikit-learn==1.4.0  # K-Means, AHP
pandas==2.2.0
numpy==1.26.4
joblib==1.3.2  # 模型序列化
scipy==1.12.0

# 深度学习框架（选择其一）
torch==2.2.0  # PyTorch（推荐，灵活性高）

# 自然语言处理
jieba==0.42.1  # 中文分词
transformers==4.37.0  # 预训练模型
sentencepiece==0.1.99  # 分词器
pytorch-transformers==1.1.0  # 兼容性

# 计算机视觉
opencv-python==4.9.0.80
Pillow==10.2.0

# 数据处理与缓存
redis==5.0.1  # 缓存层（可选）

# 开发与测试
pytest==7.4.4
pytest-asyncio==0.21.1
httpx-mock==0.10.0
black==23.12.1
ruff==0.1.9

# 监控与日志
loguru==0.7.2
prometheus-fastapi-instrumentator==6.1.0
```

### 4.2 核心模块设计要点

#### 4.2.1 生命周期管理（src/core/lifespan.py）
- **应用预热**: 启动时并行加载关键模型
- **优先级控制**: 高优先级模型立即加载，中等优先级后台加载
- **优雅关闭**: 清理资源，保存缓存

#### 4.2.2 模型管理器（src/services/model_manager.py）
- **三级缓存**: OSS云端 → 磁盘缓存 → 内存单例
- **智能预加载**: 根据配置自动预热高频使用模型
- **版本控制**: 时间戳版本，支持回滚
- **内存管理**: 监控内存使用，自动清理旧模型

#### 4.2.3 数据清洗处理器（src/utils/data_processor.py）
- **空值处理**: 多种插补策略（均值、中位数、众数、常数）
- **异常检测**: 统计方法识别异常值
- **特征工程**: 自动提取活动特征向量
- **归一化**: 指标值统一到[0,1]范围

#### 4.2.4 错误处理体系（src/core/exceptions.py）
- **分层异常**: 基础异常 → 业务异常 → 技术异常
- **丰富元数据**: 错误码、详细描述、上下文信息
- **监控集成**: 自动记录错误指标到Prometheus

## 5. 部署与监控

### 5.1 Docker配置
- **多阶段构建**: 减少镜像大小，分离构建与运行环境
- **生产优化**: 使用uvloop和httptools提高性能
- **健康检查**: 多层健康检查，确保服务可用性
- **非root用户**: 提高安全性，遵循最小权限原则

### 5.2 监控体系
- **Prometheus**: 采集性能指标和业务指标
- **Grafana**: 可视化仪表盘，实时监控
- **告警规则**: 基于阈值的智能告警
- **日志聚合**: 结构化日志，便于查询分析

### 5.3 部署脚本
- **环境检查**: 自动验证部署条件
- **一键部署**: 支持开发、测试、生产环境
- **健康验证**: 部署后自动运行测试
- **版本管理**: 自动清理旧版本镜像

## 6. 扩展性考虑

### 6.1 性能扩展
- **水平扩展**: 无状态设计，支持多实例部署
- **缓存策略**: Redis分布式缓存支持
- **异步处理**: 支持Celery异步任务队列
- **批量处理**: 支持批量API调用，提高吞吐量

### 6.2 功能扩展
- **算法插件**: 模块化设计，易于添加新算法
- **模型热更新**: 支持不停机模型更新
- **A/B测试**: 多版本模型同时在线
- **特性开关**: 配置控制功能启用/禁用

### 6.3 运维扩展
- **配置中心**: 支持动态配置更新
- **服务发现**: 集成Consul或Eureka
- **链路追踪**: 支持OpenTelemetry分布式追踪
- **混沌工程**: 故障注入测试

## 7. 非功能需求

### 7.1 性能指标
- **响应时间**: P95 < 2秒，P99 < 5秒
- **吞吐量**: 支持100 QPS并发请求
- **可用性**: 99.9%服务可用性
- **资源使用**: 内存 < 4GB，CPU < 2核（典型负载）

### 7.2 安全要求
- **认证授权**: JWT Token验证，RBAC权限控制
- **数据加密**: HTTPS传输加密，敏感数据加密存储
- **输入验证**: 严格的输入校验，防止注入攻击
- **审计日志**: 完整操作日志，支持溯源

### 7.3 可维护性
- **代码质量**: 单元测试覆盖率 > 80%
- **文档完整**: API文档、部署文档、运维手册
- **监控告警**: 完善的监控和告警体系
- **回滚机制**: 支持快速回滚到上一版本

## 8. 实施计划建议

### 8.1 阶段一：基础框架搭建（2周）
1. 项目结构初始化
2. FastAPI基础框架搭建
3. 配置管理系统
4. 基础监控和日志

### 8.2 阶段二：核心算法实现（3周）
1. K-Means推荐算法
2. AHP评估算法
3. 数据清洗和处理管道
4. 模型管理服务

### 8.3 阶段三：高级算法集成（2周）
1. NLP情感分析
2. LSTM时间序列预测
3. 遗传算法优化
4. 计算机视觉分析

### 8.4 阶段四：部署与优化（1周）
1. 生产环境部署
2. 性能测试和调优
3. 监控告警配置
4. 文档完善

## 9. 风险评估与缓解

### 9.1 技术风险
- **模型精度不足**: 准备多个备选算法，支持A/B测试
- **性能瓶颈**: 设计可扩展架构，支持缓存和异步处理
- **集成问题**: 定义清晰接口契约，使用契约测试

### 9.2 运维风险
- **模型更新故障**: 实现蓝绿部署，支持快速回滚
- **服务依赖故障**: 设计降级策略，缓存关键数据
- **监控盲点**: 多层次监控，定期演练告警

### 9.3 安全风险
- **数据泄露**: 严格权限控制，数据加密存储
- **API滥用**: 实现速率限制，API密钥管理
- **模型投毒**: 输入数据验证，模型完整性检查

## 10. 成功标准

### 10.1 功能标准
- [ ] 所有算法接口按设计实现
- [ ] 接口响应符合JSON契约
- [ ] 模型管理功能正常工作
- [ ] 监控和告警系统可用

### 10.2 性能标准
- [ ] P95响应时间 < 2秒
- [ ] 支持100 QPS并发
- [ ] 服务可用性 > 99.9%
- [ ] 内存使用 < 预期值

### 10.3 质量标准
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过率 100%
- [ ] 代码审查无严重问题
- [ ] 文档完整性和准确性

---

**设计评审**: ✅ 已通过用户审查  
**下一步**: 转入实施计划制定阶段