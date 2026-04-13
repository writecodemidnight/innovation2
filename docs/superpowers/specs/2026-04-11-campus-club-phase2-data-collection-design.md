# 校园社团活动评估系统 - 第二阶段设计文档

## 数据采集与清洗（第2-3个月）

### 1. 阶段概述

**阶段名称**：数据采集与清洗

**核心目标**：没有数据，算法就是空壳。这是构建底层数据底座的第一场硬仗。

**核心原则**：
1. **数据质量优先**：脏数据进，脏结果出
2. **多源互补**：内部数据+外部数据+模拟数据三位一体
3. **可扩展架构**：ETL流程支持未来新增数据源

---

### 2. 数据源架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                        数据源层                                   │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│  教务系统    │  学工系统    │  历史数据   │    外部网络数据      │
│  (模拟)     │  (模拟)     │  (Excel)   │  (爬虫采集)         │
└──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │                 │
       └─────────────┴─────────────┴─────────────────┘
                           │
                    ┌──────▼──────┐
                    │  ETL管道层   │
                    │  (Python)   │
                    └──────┬──────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────▼──────┐    ┌───────▼───────┐   ┌──────▼──────┐
│ PostgreSQL  │    │   MinIO/OSS   │   │  Feature    │
│ 业务数据库   │    │   文件存储    │   │   Store     │
└─────────────┘    └───────────────┘   └─────────────┘
```

---

### 3. 多源数据打通与模拟构建

#### 3.1 内部系统对接（模拟层）

由于实际学校系统无法直接对接，采用**模拟数据生成器**方式：

**设计思路**：
- 基于真实学校场景的业务规则生成模拟数据
- 数据分布符合统计学规律（正态分布、泊松分布等）
- 保留关键关联关系（学生-社团-活动三级关联）

**数据生成器组件**：

```python
# 核心生成器架构
class DataGenerator:
    ├── StudentGenerator      # 学生基础信息生成
    ├── ClubGenerator         # 社团信息生成
    ├── ActivityGenerator     # 活动数据生成
    ├── ResourceGenerator     # 场地资源生成
    └── RelationshipGenerator # 关联关系生成
```

**数据规模设计**：
| 数据类型 | 数量级 | 说明 |
|---------|-------|------|
| 学生用户 | 5,000-10,000 | 覆盖多届学生 |
| 社团组织 | 50-100 | 多种类型社团 |
| 历史活动 | 500-1000 | 近2年历史数据 |
| 场地资源 | 20-50 | 校内可用场地 |
| 活动参与记录 | 10,000+ | 参与报名记录 |

#### 3.2 历史数据录入模块

**支持格式**：
- Excel (.xlsx, .xls)
- CSV
- JSON

**数据清洗规则**：
```python
# 核心校验规则
VALIDATION_RULES = {
    "activity": {
        "required_fields": ["activity_name", "club_id", "start_time", "end_time"],
        "date_format": "%Y-%m-%d %H:%M:%S",
        "max_duration_hours": 12,
        "participants_range": (5, 500)
    },
    "budget": {
        "amount_range": (0, 100000),
        "currency": "CNY"
    }
}
```

#### 3.3 外部反馈采集（爬虫系统）

**采集目标**：
- 学校贴吧活动讨论帖
- 社团公众号文章及评论
- 微博相关话题

**采集内容**：
```python
# 情感分析语料结构
SocialMediaPost = {
    "post_id": str,           # 帖子唯一ID
    "platform": str,          # 来源平台
    "content": str,           # 文本内容
    "publish_time": datetime, # 发布时间
    "sentiment_label": int,   # 情感标签(-1,0,1)
    "activity_mentioned": str, # 提及的活动名称
    "engagement": {           # 互动数据
        "likes": int,
        "comments": int,
        "shares": int
    }
}
```

**反爬策略**：
- 请求频率控制（1-3秒间隔）
- User-Agent轮换
- IP代理池（可选）
- 数据本地缓存避免重复请求

---

### 4. 数据预处理架构

#### 4.1 清洗流水线

```
原始数据 → 格式标准化 → 缺失值处理 → 异常值检测 → 特征工程 → 干净数据
    │           │            │            │            │
    │      (Pandas)     (插值/删除)   (3σ/Z-score)  (向量化)
    │           │            │            │            │
    └───────────┴────────────┴────────────┴────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   数据质量报告     │
                    │  (数据分布/质量分) │
                    └───────────────────┘
```

#### 4.2 核心处理模块

**模块1: 数据清洗器 (DataCleaner)**
```python
class DataCleaner:
    """通用数据清洗器"""

    def handle_missing_values(df, strategy='auto'):
        """
        缺失值处理策略：
        - numeric: 中位数填充
        - categorical: 众数填充
        - datetime: 前后值插值
        - text: 空字符串填充
        """

    def detect_outliers(df, method='iqr'):
        """
        异常值检测：
        - IQR方法：Q1 - 1.5*IQR, Q3 + 1.5*IQR
        - Z-score: |z| > 3
        - Isolation Forest: 机器学习检测
        """

    def normalize_formats(df, schema):
        """统一数据格式"""
```

**模块2: 文本处理器 (TextProcessor)**
```python
class TextProcessor:
    """NLP预处理"""

    def tokenize(text, method='jieba'):
        """中文分词"""

    def vectorize(tokens, method='tfidf'):
        """文本向量化"""

    def extract_keywords(text, top_k=10):
        """关键词提取"""

    def sentiment_analysis(text):
        """情感分析（基础版）"""
```

**模块3: 特征工程器 (FeatureEngineer)**
```python
class FeatureEngineer:
    """特征工程"""

    def time_features(datetime_col):
        """时间特征提取：小时、星期、月份、是否周末"""

    def interaction_features(df, cols):
        """交互特征生成"""

    def encoding(df, cat_cols, method='onehot'):
        """分类变量编码"""
```

#### 4.3 数据质量评分系统

```python
# 质量评分维度
DATA_QUALITY_METRICS = {
    "completeness": 0.25,   # 完整度：字段填充率
    "accuracy": 0.25,       # 准确度：符合业务规则
    "consistency": 0.20,    # 一致性：关联数据匹配
    "timeliness": 0.15,     # 时效性：数据更新频率
    "validity": 0.15        # 有效性：格式/类型正确
}

# 评分等级
QUALITY_LEVELS = {
    "excellent": (90, 100),  # 优秀
    "good": (75, 90),        # 良好
    "acceptable": (60, 75),  # 可接受
    "poor": (0, 60)          # 差，需要重新采集
}
```

---

### 5. ETL管道设计

#### 5.1 批处理ETL（Apache Airflow风格）

```python
# ETL任务DAG
etl_dag = {
    "extract": [
        "extract_student_data",
        "extract_club_data",
        "extract_activity_data",
        "scrape_social_media"
    ],
    "transform": [
        "clean_student_data",
        "clean_club_data",
        "clean_activity_data",
        "analyze_sentiment",
        "generate_features"
    ],
    "load": [
        "load_to_postgres",
        "load_to_analytics_schema",
        "update_vector_store"
    ]
}
```

#### 5.2 增量同步机制

```python
class IncrementalSync:
    """基于时间戳的增量同步"""

    def __init__(self, watermark_table='etl_watermarks'):
        self.watermark_table = watermark_table

    def get_last_sync_time(self, source_name):
        """获取上次同步时间"""

    def sync_incremental(self, source, target):
        """
        1. 读取last_sync_time
        2. 查询updated_at > last_sync_time的数据
        3. 应用变更到目标
        4. 更新watermark
        """
```

---

### 6. 数据存储设计

#### 6.1 PostgreSQL业务表（扩展）

```sql
-- 外部数据采集表
CREATE TABLE social_media_posts (
    id BIGSERIAL PRIMARY KEY,
    post_id VARCHAR(100) UNIQUE NOT NULL,
    platform VARCHAR(50) NOT NULL,  -- weibo, tieba, wechat
    content TEXT NOT NULL,
    publish_time TIMESTAMP NOT NULL,
    sentiment_score DECIMAL(4,3),   -- -1.0 到 1.0
    sentiment_label VARCHAR(20),    -- positive, neutral, negative
    activity_mentioned VARCHAR(200),
    engagement_json JSONB,          -- 互动数据
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB                  -- 原始数据备份
);

-- 数据导入任务记录
CREATE TABLE data_import_jobs (
    id BIGSERIAL PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL,   -- historical, incremental
    file_name VARCHAR(500),
    records_total INTEGER,
    records_success INTEGER,
    records_failed INTEGER,
    quality_score INTEGER,           -- 0-100
    error_log JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20)               -- running, success, failed
);

-- ETL水位线表
CREATE TABLE etl_watermarks (
    source_name VARCHAR(100) PRIMARY KEY,
    last_sync_time TIMESTAMP NOT NULL,
    record_count BIGINT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 6.2 向量存储（用于NLP）

```python
# ChromaDB / FAISS 存储结构
VectorStore = {
    "collection_name": "activity_sentiments",
    "embeddings": "text2vec-base-chinese",  # 中文embedding模型
    "documents": [text_content],
    "metadatas": [{
        "activity_id": str,
        "sentiment_label": str,
        "publish_time": datetime,
        "platform": str
    }]
}
```

---

### 7. 监控与告警

#### 7.1 数据质量监控

```python
# 监控指标
MONITORING_METRICS = {
    "daily_records": "每日新增记录数",
    "quality_score": "数据质量评分",
    "sync_latency": "同步延迟时间",
    "error_rate": "错误率",
    "missing_rate": "缺失值比例"
}

# 告警规则
ALERT_RULES = [
    {"metric": "quality_score", "operator": "<", "threshold": 70},
    {"metric": "sync_latency", "operator": ">", "threshold": 3600},  # 1小时
    {"metric": "error_rate", "operator": ">", "threshold": 0.05}     # 5%
]
```

#### 7.2 数据血缘追踪

```python
# 记录数据来源和处理过程
DataLineage = {
    "source": "教务处模拟数据",
    "extraction_time": "2024-01-15 10:00:00",
    "transformations": [
        {"step": 1, "operation": "清洗", "records_in": 1000, "records_out": 980},
        {"step": 2, "operation": "标准化", "records_in": 980, "records_out": 980},
    ],
    "destination": "analytics.activity_facts",
    "load_time": "2024-01-15 10:05:00"
}
```

---

### 8. 技术栈选型

| 功能 | 技术选型 | 说明 |
|-----|---------|------|
| 数据生成 | Faker + 自定义规则 | 模拟真实数据分布 |
| 爬虫框架 | Scrapy / Playwright | 动态页面支持 |
| 数据处理 | Pandas + NumPy | 核心数据处理 |
| NLP处理 | Jieba + Scikit-learn | 中文分词与向量化 |
| 向量存储 | ChromaDB | 轻量级向量数据库 |
| 任务调度 | APScheduler / Airflow | ETL任务编排 |
| 数据验证 | Great Expectations | 数据质量检查 |
| 监控 | Prometheus + Grafana | 指标监控可视化 |

---

### 9. 实施里程碑

#### Month 2: 数据基础设施建设
- Week 1-2: 模拟数据生成器开发
- Week 3: 历史数据导入模块
- Week 4: 基础ETL管道

#### Month 3: 外部数据采集与清洗
- Week 1-2: 爬虫系统开发
- Week 3: NLP预处理管道
- Week 4: 数据质量监控与优化

---

### 10. 风险与应对

| 风险 | 概率 | 影响 | 应对策略 |
|-----|-----|------|---------|
| 模拟数据分布不真实 | 中 | 高 | 与实际学校数据对比校准 |
| 反爬策略升级 | 中 | 中 | 多源采集+本地缓存 |
| 数据质量不达标 | 低 | 高 | 多级校验+人工抽查 |
| 处理性能瓶颈 | 中 | 中 | 分批处理+并行化 |

---

*文档版本: 1.0*
*最后更新: 2026-04-11*
*设计者: Claude Code*
*状态: 待审查*
