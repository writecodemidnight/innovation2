# 校园社团活动评估系统 - 第三阶段设计文档

## 核心算法与模型攻坚（第4-7个月）

### 1. 阶段概述

**阶段名称**: 核心算法与模型攻坚

**核心目标**: 
本阶段是项目"含金量"最高的环节，需要攻克两个核心技术壁垒：
1. **学生活动画像系统** - 使用K-Means聚类实现个性化推荐基础
2. **五维活动效果评估体系** - 使用AHP层次分析法构建客观评分模型

**技术挑战**:
- 特征工程设计与选择
- 聚类算法参数调优
- AHP一致性检验与权重合理性
- 模型可解释性与业务落地

---

### 2. 算法架构设计

```
┌─────────────────────────────────────────────────────────────────────┐
│                        算法服务层 (FastAPI)                          │
├─────────────────────┬─────────────────────┬─────────────────────────┤
│   学生活动画像系统    │   活动效果评估体系   │    模型服务管理          │
│   (K-Means聚类)      │   (AHP层次分析)      │    (训练/部署/监控)      │
├─────────────────────┼─────────────────────┼─────────────────────────┤
│ • 特征提取器         │ • 判断矩阵构建       │ • 模型版本控制           │
│ • K-Means聚类器      │ • 一致性检验         │ • 模型性能监控           │
│ • 轮廓评估          │ • 权重计算           │ • A/B测试支持            │
│ • 画像标签生成       │ • 模糊综合评价       │ • 模型回滚              │
└─────────────────────┴─────────────────────┴─────────────────────────┘
                            │
               ┌────────────┼────────────┐
               │            │            │
        ┌──────▼──────┐ ┌───▼────┐ ┌────▼─────┐
        │ PostgreSQL  │ │ Redis  │ │  Model   │
        │ 特征数据    │ │  缓存  │ │  Store   │
        └─────────────┘ └────────┘ └──────────┘
```

---

### 3. 模型1: 学生活动画像系统

#### 3.1 算法原理

**K-Means聚类算法**
- 无监督学习，将学生划分为K个兴趣群体
- 基于活动参与特征向量进行空间聚类
- 使用轮廓系数(Silhouette Score)评估聚类质量

#### 3.2 特征工程设计

**学生特征向量 (12维)**:

```python
STUDENT_FEATURES = {
    # 活动类型偏好 (5维) - 基于参与次数的TF-IDF加权
    "academic_participation": "学术类活动参与频率",
    "arts_participation": "文艺类活动参与频率",
    "sports_participation": "体育类活动参与频率",
    "public_participation": "公益类活动参与频率",
    "tech_participation": "科技类活动参与频率",

    # 时间分布特征 (3维)
    "weekend_participation_ratio": "周末参与比例",
    "evening_participation_ratio": "晚间参与比例",
    "avg_participation_interval": "平均参与间隔(天)",

    # 参与度特征 (2维)
    "total_participations": "总参与次数",
    "avg_rating_given": "平均评分倾向",

    # 社交特征 (2维)
    "club_membership_count": "加入社团数量",
    "organizer_ratio": "作为组织者比例"
}
```

#### 3.3 聚类群体标签定义

| 群体标签 | 特征描述 | 典型行为 |
|---------|---------|---------|
| **学术先锋型** | 学术类参与高，周末活动多 | 专注学术讲座、科研竞赛 |
| **文艺活跃型** | 文艺类参与高，晚间活动多 | 参加演出、展览、创作活动 |
| **运动健将型** | 体育类参与高，频次稳定 | 热衷各类体育赛事、训练 |
| **公益热心型** | 公益类参与高，组织者比例高 | 志愿服务、支教、环保活动 |
| **科技极客型** | 科技类参与高，创新性强 | 编程比赛、技术分享、创客活动 |
| **社交蝴蝶型** | 多社团成员，各类活动均有参与 | 广泛参与，跨社团交流 |
| **被动参与型** | 总体参与少，间隔长 | 偶尔参与，被动接收信息 |

#### 3.4 模型训练流程

```
1. 数据准备
   └─> 从数据库查询学生参与记录
   └─> 计算12维特征向量
   └─> 数据标准化 (StandardScaler)

2. 最优K值选择
   └─> 肘部法则 (Elbow Method)
   └─> 轮廓系数评估 (Silhouette Analysis)
   └─> 选择最佳 K ∈ [4, 8]

3. 模型训练
   └─> K-Means 聚类 (n_clusters=K, random_state=42)
   └─> 聚类中心保存
   └─> 标签映射建立

4. 模型评估
   └─> 轮廓系数 > 0.5 (良好分离)
   └─> 类内距离 < 类间距离
   └─> 业务可解释性验证
```

---

### 4. 模型2: 五维活动效果评估体系

#### 4.1 AHP层次分析法原理

**层次结构**:
```
目标层: 活动效果综合评价 (A)
    │
准则层: ├─ 参与度 (B1) ──┬─ 参与人数 (C1)
       │               ├─ 报名率 (C2)
       │               └─ 实际到场率 (C3)
       │
       ├─ 教育性 (B2) ──┬─ 知识获取度 (C4)
       │               ├─ 技能提升度 (C5)
       │               └─ 满意度评分 (C6)
       │
       ├─ 创新性 (B3) ──┬─ 活动形式新颖度 (C7)
       │               ├─ 内容原创性 (C8)
       │               └─ 技术应用度 (C9)
       │
       ├─ 影响力 (B4) ──┬─ 社交媒体曝光量 (C10)
       │               ├─ 口碑传播度 (C11)
       │               └─ 后续影响持续期 (C12)
       │
       └─ 可持续性 (B5) ─┬─ 资源利用率 (C13)
                       ├─ 经验可复制性 (C14)
                       └─ 预期复办指数 (C15)
```

#### 4.2 判断矩阵构建

**准则层判断矩阵** (B1-B5 相对于 A):

| A | B1(参与) | B2(教育) | B3(创新) | B4(影响) | B5(可持续) |
|---|---------|---------|---------|---------|-----------|
| B1 | 1 | 1/2 | 2 | 1/3 | 2 |
| B2 | 2 | 1 | 3 | 1/2 | 3 |
| B3 | 1/2 | 1/3 | 1 | 1/4 | 1 |
| B4 | 3 | 2 | 4 | 1 | 4 |
| B5 | 1/2 | 1/3 | 1 | 1/4 | 1 |

**标度说明**:
- 1: 同等重要
- 3: 稍微重要
- 5: 明显重要
- 7: 强烈重要
- 9: 极端重要
- 倒数: 反比较

#### 4.3 一致性检验

**计算步骤**:
1. 计算判断矩阵最大特征值 λ_max
2. 计算一致性指标 CI = (λ_max - n) / (n - 1)
3. 查表得随机一致性指标 RI
4. 计算一致性比例 CR = CI / RI
5. **通过标准**: CR < 0.1

#### 4.4 模糊综合评价

**评价等级**:
```
V = {优秀(90-100), 良好(80-89), 中等(70-79), 及格(60-69), 不及格(0-59)}
```

**评价步骤**:
1. 建立模糊评价矩阵 R (指标×等级)
2. 确定权重向量 W (AHP计算结果)
3. 模糊合成: B = W ∘ R
4. 计算综合得分: S = B × V^T

#### 4.5 输出格式

```python
{
    "activity_id": "ACT12345",
    "overall_score": 85.6,  # 综合得分
    "radar_data": {
        "参与度": 88.0,
        "教育性": 82.5,
        "创新性": 75.0,
        "影响力": 90.0,
        "可持续性": 80.0
    },
    "dimension_weights": {
        "参与度": 0.20,
        "教育性": 0.30,
        "创新性": 0.15,
        "影响力": 0.25,
        "可持续性": 0.10
    },
    "ahp_consistency": {
        "cr": 0.043,  # 一致性比例
        "passed": True
    },
    "evaluation_level": "良好"  # 等级评定
}
```

---

### 5. API接口设计

#### 5.1 学生活动画像接口

```python
# POST /api/v1/ml/student-portrait/analyze
{
    "student_ids": ["20210001", "20210002"],  # 可选，空则分析所有
    "n_clusters": null,  # 可选，自动选择最佳K
    "retrain": false     # 是否强制重训练
}

# Response
{
    "success": true,
    "data": {
        "model_id": "kmeans_v20240412_001",
        "n_clusters": 6,
        "silhouette_score": 0.68,
        "students": [
            {
                "student_id": "20210001",
                "cluster_id": 2,
                "cluster_label": "文艺活跃型",
                "features": {...},
                "confidence": 0.85
            }
        ]
    }
}
```

#### 5.2 活动效果评估接口

```python
# POST /api/v1/ml/activity-evaluation/evaluate
{
    "activity_id": "ACT12345",
    "metrics": {  # 可选，系统会自动查询
        "participation_count": 120,
        "registration_rate": 0.85,
        "actual_attendance_rate": 0.92,
        ...
    }
}

# Response
{
    "success": true,
    "data": {
        "activity_id": "ACT12345",
        "overall_score": 85.6,
        "radar_data": {...},
        "ahp_weights": {...},
        "consistency_check": {...}
    }
}

# POST /api/v1/ml/activity-evaluation/batch
# 批量评估多个活动
```

#### 5.3 模型管理接口

```python
# GET /api/v1/ml/models  # 列出所有模型
# GET /api/v1/ml/models/{model_id}  # 获取模型详情
# POST /api/v1/ml/models/{model_id}/retrain  # 重训练模型
# POST /api/v1/ml/models/{model_id}/evaluate  # 评估模型性能
```

---

### 6. 数据库表设计

```sql
-- 学生画像表
CREATE TABLE student_portraits (
    id BIGSERIAL PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL UNIQUE,
    cluster_id INTEGER,
    cluster_label VARCHAR(50),
    feature_vector JSONB NOT NULL,
    confidence DECIMAL(3,2),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 活动评估结果表
CREATE TABLE activity_evaluations (
    id BIGSERIAL PRIMARY KEY,
    activity_id VARCHAR(20) NOT NULL UNIQUE,
    overall_score DECIMAL(5,2),
    dimension_scores JSONB NOT NULL,  -- 五维得分
    dimension_weights JSONB NOT NULL, -- AHP权重
    ahp_consistency_ratio DECIMAL(4,3),
    evaluation_level VARCHAR(20),
    model_version VARCHAR(50),
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 聚类模型元数据
CREATE TABLE ml_clustering_models (
    id BIGSERIAL PRIMARY KEY,
    model_id VARCHAR(50) PRIMARY KEY,
    model_type VARCHAR(50),
    n_clusters INTEGER,
    silhouette_score DECIMAL(4,3),
    cluster_centers JSONB,
    feature_names JSONB,
    training_data_count INTEGER,
    trained_at TIMESTAMP,
    is_active BOOLEAN DEFAULT false
);

-- AHP模型配置表
CREATE TABLE ml_ahp_configs (
    id BIGSERIAL PRIMARY KEY,
    config_id VARCHAR(50) PRIMARY KEY,
    judgment_matrix JSONB NOT NULL,
    calculated_weights JSONB NOT NULL,
    consistency_ratio DECIMAL(4,3),
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 7. 模型评估与验证

#### 7.1 K-Means评估指标

| 指标 | 目标值 | 说明 |
|-----|-------|------|
| 轮廓系数 | > 0.5 | 聚类分离度良好 |
| CH指数 | > 100 | 类间分离显著 |
| DB指数 | < 1.0 | 类内紧凑度高 |
| 类大小均衡度 | 1:5 | 最大类:最小类不超过5倍 |

#### 7.2 AHP验证标准

| 检验项 | 标准 | 说明 |
|-------|------|------|
| CR < 0.1 | 通过 | 一致性检验通过 |
| 权重和 = 1 | 是 | 权重归一化验证 |
| 维度覆盖 | 完整 | 无遗漏维度 |
| 业务合理性 | 确认 | 专家审核通过 |

#### 7.3 业务验证

- **画像准确性**: 抽样验证学生画像与实际行为的一致性
- **评分合理性**: 历史高分活动与评估结果的相关性
- **稳定性测试**: 同一数据多次评估结果波动 < 5%

---

### 8. 技术栈与依赖

```txt
# 核心算法
scikit-learn==1.4.0      # K-Means聚类
numpy==1.26.4            # 数值计算
scipy==1.12.0            # 科学计算

# AHP/模糊评价
ahpy==2.0.1              # AHP层次分析

# 模型持久化
joblib==1.3.2            # 模型序列化

# API服务
fastapi==0.104.1         # API框架
pydantic==2.5.3          # 数据验证
```

---

### 9. 风险与应对

| 风险 | 概率 | 影响 | 应对策略 |
|-----|------|------|---------|
| 聚类效果不佳 | 中 | 高 | 特征工程迭代、尝试DBSCAN等替代算法 |
| AHP判断矩阵不一致 | 低 | 中 | 专家咨询修正、Saaty一致性调整 |
| 特征数据缺失 | 中 | 中 | 缺失值填充策略、特征选择鲁棒性 |
| 模型过拟合 | 低 | 中 | 交叉验证、正则化、数据增强 |
| 计算性能瓶颈 | 低 | 低 | 缓存策略、异步计算、分批处理 |

---

### 10. 实施里程碑

#### Month 4: 学生活动画像系统
- Week 1: 特征工程设计与实现
- Week 2: K-Means聚类算法开发
- Week 3: 最优K值选择与模型评估
- Week 4: API接口与集成测试

#### Month 5: 五维评估体系
- Week 1: AHP判断矩阵设计与一致性检验
- Week 2: 权重计算与模糊评价实现
- Week 3: 雷达图数据生成与可视化
- Week 4: 业务验证与专家审核

#### Month 6-7: 模型优化与集成
- 模型性能监控体系
- 模型自动重训练机制
- 与推荐系统联动
- 算法文档与知识沉淀

---

## 模型3: 资源需求预测模型

### 3.1 算法原理

**多算法融合预测**
- **时间序列分析**: ARIMA/SARIMA 处理季节性、趋势性
- **机器学习**: 随机森林、XGBoost 处理多特征非线性关系
- **深度学习**: LSTM 捕捉长期依赖模式

**Apriori关联规则挖掘**
- 挖掘"活动类型 - 资源消耗"的关联规则
- 支持度、置信度、提升度评估规则强度

### 3.2 预测维度

| 预测对象 | 算法选择 | 特征输入 |
|---------|---------|---------|
| **场地需求** | ARIMA + 随机森林 | 历史使用率、活动类型分布、季节因素 |
| **资金需求** | LSTM + XGBoost | 历史支出、活动规模、物价指数 |
| **人力需求** | 随机森林 | 活动频次、参与人数、组织者负荷 |

### 3.3 特征工程

```python
RESOURCE_PREDICTION_FEATURES = {
    # 时间特征
    "month": "月份(1-12)",
    "week_of_year": "周次(1-52)",
    "is_holiday": "是否节假日",
    "is_exam_period": "是否考试周",

    # 历史统计特征
    "avg_venue_usage_30d": "30天平均场地使用率",
    "avg_budget_30d": "30天平均预算",
    "activity_count_30d": "30天活动数量",

    # 活动分布特征
    "academic_ratio": "学术类活动占比",
    "arts_ratio": "文艺类活动占比",
    "sports_ratio": "体育类活动占比",

    # 外部因素
    "temperature": "平均气温",
    "rainy_days": "雨天数量",
    "school_event_count": "校内大型活动数",
}
```

### 3.4 Apriori关联规则

**挖掘目标**:
```
规则形式: {活动类型=A, 参与规模=大} => {场地需求=体育馆, 资金需求=高}
支持度: P(A ∪ B) > 0.05
置信度: P(B|A) > 0.6
提升度: Lift > 1.2
```

### 3.5 输出格式

```python
{
    "prediction_id": "PRED20240412",
    "target_month": "2024-05",
    "venue_prediction": {
        "predicted_demand_hours": 320,
        "confidence_interval": [280, 360],
        "peak_days": ["2024-05-15", "2024-05-20"],
        "model_used": "sarima"
    },
    "budget_prediction": {
        "predicted_amount": 45000,
        "confidence_interval": [40000, 50000],
        "breakdown_by_type": {...}
    },
    "association_rules": [
        {
            "antecedent": ["academic", "large_scale"],
            "consequent": ["high_budget", "lecture_hall"],
            "support": 0.08,
            "confidence": 0.72,
            "lift": 1.45
        }
    ]
}
```

---

## 模型4: 智能资源调度算法

### 4.1 算法原理

**遗传算法 (Genetic Algorithm)**
- **编码方案**: 实数编码，表示资源分配方案
- **目标函数**: 多目标优化 (资源利用率最大化 + 活动效果得分最大化)
- **约束处理**: 惩罚函数法处理硬约束

**多目标优化框架**
```
最大化: F(x) = [f1(x), f2(x)]
  f1(x) = 资源利用率 (venue_utilization + budget_efficiency) / 2
  f2(x) = 活动效果得分 (AHP评分加权平均)

约束:
  g1(x): 场地时间冲突 = 0
  g2(x): 预算 ≤ 可用预算
  g3(x): 每个活动分配的资源 ≥ 最低需求
```

### 4.2 GA算法设计

**染色体编码**:
```python
# 每个基因代表一个活动的资源分配
Chromosome = [
    {
        "activity_id": "ACT001",
        "venue_id": "VENUE_A101",
        "venue_time_slot": "2024-05-15T14:00",
        "budget_allocated": 5000,
        "staff_assigned": ["STAFF_001", "STAFF_002"]
    },
    # ... 更多活动
]
```

**遗传算子**:
| 算子 | 方法 | 概率 |
|-----|------|-----|
| 选择 | 锦标赛选择 (Tournament) | - |
| 交叉 | 均匀交叉 (Uniform Crossover) | 0.8 |
| 变异 | 高斯变异 + 边界修复 | 0.1 |
| 精英保留 | 保留前10%最优个体 | - |

**适应度函数**:
```python
def fitness(chromosome):
    # 资源利用率得分 (0-100)
    utilization_score = calculate_resource_utilization(chromosome)

    # 活动效果得分 (0-100)
    effect_score = calculate_activity_effect(chromosome)

    # 约束惩罚
    penalty = calculate_constraint_violation(chromosome) * 100

    # 综合适应度 (NSGA-II风格)
    return (utilization_score + effect_score) / 2 - penalty
```

### 4.3 调度约束条件

**硬约束 (必须满足)**:
1. 同一时间段同一 venue 只能分配给一个活动
2. 预算总和 ≤ 可用预算
3. 活动必须分配在其可接受的时间段内
4. 必需的人员配置必须满足

**软约束 (尽量满足)**:
1. 高优先级活动优先分配优质资源
2. 相似活动时间上尽量分散
3. 场地利用率均衡

### 4.4 输出格式

```python
{
    "schedule_id": "SCH20240412",
    "optimization_metrics": {
        "resource_utilization": 0.85,
        "avg_activity_score": 82.5,
        "constraint_satisfaction": 1.0,  # 所有硬约束满足
        "fitness_score": 83.8
    },
    "assignments": [
        {
            "activity_id": "ACT001",
            "activity_name": "校园歌手大赛",
            "venue": {"id": "VENUE_A101", "name": "大礼堂"},
            "time_slot": {"start": "2024-05-15T18:00", "end": "2024-05-15T21:00"},
            "budget_allocated": 8000,
            "staff": [{"id": "STAFF_001", "name": "张三", "role": "现场协调"}],
            "expected_score": 88.5
        }
    ],
    "unscheduled": [],  # 无法安排的活动列表
    "generation_stats": {
        "total_generations": 500,
        "convergence_generation": 380,
        "final_population_size": 100
    }
}
```

### 4.5 算法流程

```
1. 初始化种群 (随机生成可行解)
   └─> 种群大小: 100
   └─> 使用贪心算法生成初始可行解

2. 评估适应度
   └─> 计算每个个体的目标函数值
   └─> 检查约束违反情况

3. 迭代优化 (最大500代)
   ├─> 选择: 锦标赛选择 (tournament size=3)
   ├─> 交叉: 均匀交叉 (概率0.8)
   ├─> 变异: 高斯变异 (概率0.1)
   ├─> 精英保留: 前10%直接进入下一代
   └─> 边界修复: 确保解在可行域内

4. 收敛判断
   └─> 连续50代最优解无改进则停止
   └─> 或达到最大代数

5. 输出最优解
   └─> 解码染色体为资源分配方案
   └─> 生成调度报告
```

---

*文档版本: 2.0*
*最后更新: 2026-04-12*
*设计者: Claude Code*
*状态: 待实施*
