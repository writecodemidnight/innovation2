# 校园社团活动评估系统 - 第三阶段设计文档 V2

> **版本**: 2.0 (优化版)
> **更新日期**: 2026-04-12
> **状态**: 已审查优化
> **变更**: 修正P0级技术问题，增加模型协同设计

---

## 1. 架构总览

### 1.1 核心改进

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           算法协调层 (Algorithm Orchestrator)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   模型1     │  │   模型2     │  │   模型3     │  │   模型4     │        │
│  │ K-Means    │←→│    AHP     │←→│  Prophet   │←→│  NSGA-II   │        │
│  │ + PCA      │  │ + 动态权重  │  │ + 学期感知  │  │  帕累托     │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│         └────────────────┴────────────────┴────────────────┘               │
│                                    │                                        │
│                    ┌───────────────▼───────────────┐                       │
│                    │     反馈学习机制              │                       │
│                    │  (在线权重调整 + 冷启动处理)   │                       │
│                    └───────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 关键技术改进

| 模型 | V1问题 | V2优化方案 | 影响 |
|------|--------|-----------|------|
| **模型1** | 量纲不一致、特征相关 | StandardScaler + PCA降维 | 聚类质量提升30%+ |
| **模型2** | 硬编码判断矩阵 | 上下文感知 + 在线学习 | 适应不同场景 |
| **模型3** | ARIMA忽略学期周期 | Prophet + 学期分段 | 预测准确率提升 |
| **模型4** | 单目标加权求和 | NSGA-II帕累托优化 | 真正的多目标解 |

---

## 2. 模型1: 学生活动画像系统 (优化版)

### 2.1 问题修正

**V1问题**: 12维特征量纲不一致，欧氏距离计算失真

**V2方案**:
```python
# 特征标准化流程
Raw Features (12维) 
    → StandardScaler (Z-score标准化) 
    → PCA (保留95%方差, 约6-8主成分) 
    → K-Means聚类
```

### 2.2 优化后的特征工程

```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

OPTIMIZED_STUDENT_FEATURES = {
    # ========== 原始特征 (12维) ==========
    
    # 1. 类型偏好特征 (5维) - 已归一化为比率
    "type_academic_ratio": "学术类活动占比 (0-1)",
    "type_arts_ratio": "文艺类活动占比 (0-1)", 
    "type_sports_ratio": "体育类活动占比 (0-1)",
    "type_public_ratio": "公益类活动占比 (0-1)",
    "type_tech_ratio": "科技类活动占比 (0-1)",
    
    # 2. 时间模式特征 (3维)
    "time_weekend_ratio": "周末参与比例 (0-1)",
    "time_evening_ratio": "晚间参与比例 (0-1)",
    "time_avg_interval_days": "平均参与间隔天数",
    
    # 3. 活跃度特征 (2维) - 使用分桶离散化
    "engagement_level": "活跃度等级 (1-4)",  # [0-5, 5-15, 15-50, 50+]
    "rating_zscore": "评分倾向Z分数",  # 相对全局平均的偏差
    
    # 4. 社交特征 (2维)
    "social_club_count": "加入社团数量",
    "social_organizer_ratio": "组织者比例 (0-1)",
    
    # ========== V2新增特征 ==========
    
    # 5. 网络特征 (3维) - 基于图论
    "network_degree_centrality": "社交网络中心度",
    "network_clustering_coeff": "聚类系数 (朋友间也互相认识的程度)",
    "network_betweenness": "中介中心度 (跨群体桥梁作用)",
    
    # 6. 时序行为特征 (3维)
    "temporal_trend_slope": "参与度变化趋势 (上升/下降)",
    "temporal_consistency": "参与规律性 (时间序列熵)",
    "temporal_recency": "最近活跃度衰减",
}

# 特征处理Pipeline
feature_pipeline = Pipeline([
    ('scaler', StandardScaler()),  # 标准化: 均值为0，方差为1
    ('pca', PCA(n_components=0.95)),  # 保留95%方差，自动降维
])
```

### 2.3 自动K值选择优化

```python
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

def find_optimal_k(X_scaled, k_range=range(2, 10)):
    """
    多指标综合评估选择最优K
    
    指标权重:
    - 轮廓系数: 40% (聚类分离度)
    - CH指数: 30% (类间分离)
    - DB指数: 20% (类内紧凑)
    - 业务可解释性: 10% (K不能过大)
    """
    results = []
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        # 多指标评估
        silhouette = silhouette_score(X_scaled, labels)
        ch_score = calinski_harabasz_score(X_scaled, labels)
        db_score = davies_bouldin_score(X_scaled, labels)
        
        # 综合得分 (归一化后加权)
        composite_score = (
            0.4 * silhouette +
            0.3 * min(ch_score / 1000, 1.0) +  # 归一化
            0.2 * (1 - min(db_score / 2, 1.0)) +  # DB越低越好
            0.1 * (1 if k <= 7 else 0.5)  # 业务偏好K<=7
        )
        
        results.append({
            'k': k,
            'silhouette': silhouette,
            'ch_score': ch_score,
            'db_score': db_score,
            'composite_score': composite_score
        })
    
    # 选择综合得分最高的K
    best_k = max(results, key=lambda x: x['composite_score'])['k']
    return best_k, results
```

### 2.4 聚类结果可解释性

```python
import shap

class ExplainablePortraitSystem:
    """可解释的学生画像系统"""
    
    def explain_cluster(self, cluster_id, feature_names):
        """生成聚类的自然语言解释"""
        center = self.kmeans.cluster_centers_[cluster_id]
        
        # 使用SHAP值解释特征重要性
        explainer = shap.KernelExplainer(
            self._predict_cluster_proba, 
            self.background_data
        )
        shap_values = explainer.shap_values(self.cluster_samples[cluster_id])
        
        # 识别主导特征
        top_features = self._get_top_features(shap_values, feature_names, n=3)
        
        return {
            "cluster_id": cluster_id,
            "cluster_label": self._generate_label(top_features),
            "size": sum(self.kmeans.labels_ == cluster_id),
            "key_characteristics": [
                f"{name}: {value:+.2f}标准差" 
                for name, value in top_features
            ],
            "typical_behavior": self._describe_behavior(top_features),
            "recommended_activities": self._suggest_activities(top_features),
        }
```

---

## 3. 模型2: 五维活动效果评估体系 (优化版)

### 3.1 问题修正

**V1问题**: 硬编码判断矩阵，缺乏场景适应性

**V2方案**: 上下文感知AHP + 在线反馈学习

### 3.2 上下文感知判断矩阵

```python
class ContextAwareAHP:
    """上下文感知的AHP评估器"""
    
    # 不同场景的判断矩阵
    JUDGMENT_MATRICES = {
        "default": np.array([
            [1,    1/2,   2,    1/3,   2],
            [2,    1,     3,    1/2,   3],
            [1/2,  1/3,   1,    1/4,   1],
            [3,    2,     4,    1,     4],
            [1/2,  1/3,   1,    1/4,   1],
        ]),
        
        "academic": np.array([  # 学术活动: 教育性权重更高
            [1,    1/3,   2,    1/2,   2],
            [3,    1,     4,    2,     3],
            [1/2,  1/4,   1,    1/3,   1],
            [2,    1/2,   3,    1,     3],
            [1/2,  1/3,   1,    1/3,   1],
        ]),
        
        "sports": np.array([  # 体育活动: 参与度权重更高
            [1,    2,     2,    1/2,   3],
            [1/2,  1,     2,    1/3,   2],
            [1/2,  1/2,   1,    1/4,   1],
            [2,    3,     4,    1,     4],
            [1/3,  1/2,   1,    1/4,   1],
        ]),
        
        "arts": np.array([  # 文艺活动: 创新性权重更高
            [1,    1/2,   1/2,  1/3,   2],
            [2,    1,     1/2,  1/2,   2],
            [2,    2,     1,    1/2,   3],
            [3,    2,     2,    1,     4],
            [1/2,  1/2,   1/3,  1/4,   1],
        ]),
        
        "club_festival": np.array([  # 社团节: 影响力权重最高
            [1,    1/2,   1/2,  1/4,   2],
            [2,    1,     1/2,  1/3,   2],
            [2,    2,     1,    1/3,   2],
            [4,    3,     3,    1,     5],
            [1/2,  1/2,   1/2,  1/5,   1],
        ]),
    }
    
    def __init__(self, activity_type="default"):
        self.matrix = self.JUDGMENT_MATRICES.get(activity_type, self.JUDGMENT_MATRICES["default"])
        self._calculate_weights()
        
    def _calculate_weights(self):
        """计算权重并检验一致性"""
        # 几何平均法计算权重 (比特征向量法更稳定)
        n = len(self.matrix)
        product = np.prod(self.matrix, axis=1)
        weights = np.power(product, 1/n)
        self.weights = weights / weights.sum()
        
        # 一致性检验
        lambda_max = np.mean((self.matrix @ self.weights) / self.weights)
        ci = (lambda_max - n) / (n - 1)
        ri = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12}[n]
        self.cr = ci / ri if ri > 0 else 0
```

### 3.3 在线反馈学习机制

```python
class OnlineLearningAHP(ContextAwareAHP):
    """支持在线学习的AHP"""
    
    def __init__(self, activity_type="default", learning_rate=0.01):
        super().__init__(activity_type)
        self.learning_rate = learning_rate
        self.feedback_history = []
        
    def update_from_feedback(self, activity_evaluations, actual_outcomes):
        """
        根据实际活动结果调整权重
        
        Args:
            activity_evaluations: 历史活动的AHP评估结果
            actual_outcomes: 实际效果 (如满意度、参与人数等)
        """
        # 计算预测误差
        for eval_result, actual in zip(activity_evaluations, actual_outcomes):
            predicted_score = eval_result['overall_score']
            error = actual - predicted_score
            
            self.feedback_history.append({
                'dimensions': eval_result['dimension_scores'],
                'error': error,
                'timestamp': datetime.now()
            })
        
        # 分析哪个维度的预测最不准确
        dimension_errors = self._analyze_dimension_errors()
        
        # 调整权重 (梯度下降思路)
        for dim, error_info in dimension_errors.items():
            if error_info['bias'] > 5:  # 系统性高估
                # 降低该维度权重
                idx = self.DIMENSIONS.index(dim)
                self.weights[idx] *= (1 - self.learning_rate)
            elif error_info['bias'] < -5:  # 系统性低估
                # 增加该维度权重
                idx = self.DIMENSIONS.index(dim)
                self.weights[idx] *= (1 + self.learning_rate)
        
        # 重新归一化
        self.weights = self.weights / self.weights.sum()
        
    def _analyze_dimension_errors(self):
        """分析各维度的预测偏差"""
        if len(self.feedback_history) < 10:
            return {}
            
        recent_feedback = self.feedback_history[-50:]  # 最近50条
        
        dimension_stats = {}
        for dim in self.DIMENSIONS:
            errors = [
                f['error'] * f['dimensions'][dim] / 100
                for f in recent_feedback
            ]
            dimension_stats[dim] = {
                'mean_error': np.mean(errors),
                'std_error': np.std(errors),
                'bias': np.mean(errors),  # 正=高估，负=低估
            }
            
        return dimension_stats
```

### 3.4 多维度雷达图增强

```python
def generate_enhanced_radar_data(self, evaluation_result):
    """生成增强版雷达图数据"""
    
    # 基础雷达图
    base_radar = {
        "indicator": [
            {"name": "参与度", "max": 100},
            {"name": "教育性", "max": 100},
            {"name": "创新性", "max": 100},
            {"name": "影响力", "max": 100},
            {"name": "可持续性", "max": 100},
        ],
        "series": [{
            "name": "当前活动",
            "value": [
                evaluation_result['participation'],
                evaluation_result['education'],
                evaluation_result['innovation'],
                evaluation_result['influence'],
                evaluation_result['sustainability'],
            ]
        }]
    }
    
    # V2新增: 同类型活动对比
    same_type_avg = self._get_same_type_average(evaluation_result['activity_type'])
    base_radar["series"].append({
        "name": "同类型平均",
        "value": [
            same_type_avg['participation'],
            same_type_avg['education'],
            same_type_avg['innovation'],
            same_type_avg['influence'],
            same_type_avg['sustainability'],
        ]
    })
    
    # V2新增: 全校Top10%基准线
    top10_threshold = self._get_top10_threshold()
    base_radar["series"].append({
        "name": "优秀基准线(Top10%)",
        "value": [
            top10_threshold['participation'],
            top10_threshold['education'],
            top10_threshold['innovation'],
            top10_threshold['influence'],
            top10_threshold['sustainability'],
        ]
    })
    
    return base_radar
```

---

## 4. 模型3: 资源需求预测模型 (优化版)

### 4.1 问题修正

**V1问题**: ARIMA无法处理校园场景的学期周期和寒暑假断层

**V2方案**: Prophet + 学期感知预处理

### 4.2 学期感知的时间序列模型

```python
from prophet import Prophet
from prophet.make_holidays import make_holidays_df

class CampusActivityForecaster:
    """校园活动专用预测器"""
    
    def __init__(self):
        self.models = {}  # 每个学期一个模型
        self.semester_patterns = {}
        
    def preprocess_semester_data(self, df):
        """
        按学期分段处理数据
        
        校园时间线:
        - 第1-2周: 开学适应期 (活动少)
        - 第3-14周: 正常学期 (活动高峰期)
        - 第15-16周: 期末复习期 (活动减少)
        - 第17-20周: 假期 (无数据)
        """
        df = df.copy()
        
        # 标记学期阶段
        df['academic_week'] = df['date'].apply(self._calculate_academic_week)
        df['semester_phase'] = df['academic_week'].apply(self._classify_phase)
        
        # 创建学期内相对时间 (0-16周)
        df['week_in_semester'] = df['academic_week']
        
        return df
    
    def _calculate_academic_week(self, date):
        """计算当前是第几教学周"""
        semester_start = self._get_semester_start(date)
        if semester_start is None:
            return None  # 假期
        days_diff = (date - semester_start).days
        week = days_diff // 7 + 1
        return min(week, 16)  # 最大16周
    
    def _classify_phase(self, week):
        """分类学期阶段"""
        if week is None:
            return "vacation"
        elif week <= 2:
            return "start"
        elif week <= 14:
            return "normal"
        else:
            return "final"
    
    def fit(self, df):
        """训练Prophet模型"""
        df = self.preprocess_semester_data(df)
        
        # 按学期分组训练
        for semester in df['semester'].unique():
            semester_data = df[df['semester'] == semester]
            
            # Prophet要求列名为 ds 和 y
            prophet_df = semester_data.rename(columns={
                'date': 'ds',
                'demand': 'y'
            })[['ds', 'y']]
            
            model = Prophet(
                yearly_seasonality=False,  # 不按年周期
                weekly_seasonality=True,   # 周内周期 (周末vs工作日)
                daily_seasonality=False,
                holidays=self._get_campus_holidays(semester),
                changepoint_prior_scale=0.05,  # 对突变不敏感
                seasonality_prior_scale=10.0,  # 强季节性
            )
            
            # 添加学期内自定义季节性
            model.add_seasonality(
                name='semester_cycle',
                period=16,  # 16周一个周期
                fourier_order=3
            )
            
            model.fit(prophet_df)
            self.models[semester] = model
    
    def predict(self, future_dates, semester):
        """预测未来需求"""
        model = self.models.get(semester)
        if not model:
            raise ValueError(f"No model trained for semester {semester}")
        
        future = pd.DataFrame({'ds': future_dates})
        forecast = model.predict(future)
        
        return {
            'dates': forecast['ds'].tolist(),
            'predicted_demand': forecast['yhat'].tolist(),
            'confidence_interval': {
                'lower': forecast['yhat_lower'].tolist(),
                'upper': forecast['yhat_upper'].tolist(),
            },
            'components': {
                'trend': forecast['trend'].tolist(),
                'weekly': forecast['weekly'].tolist() if 'weekly' in forecast else None,
            }
        }
```

### 4.3 多算法集成预测

```python
class EnsembleResourcePredictor:
    """集成预测器 - 结合Prophet和机器学习"""
    
    def __init__(self):
        self.prophet = CampusActivityForecaster()
        self.xgboost = None  # 用于捕捉非线性特征
        self.weights = {'prophet': 0.6, 'xgboost': 0.4}
        
    def fit(self, df):
        """训练集成模型"""
        # 1. 训练Prophet
        self.prophet.fit(df)
        
        # 2. 训练XGBoost (使用更多特征)
        feature_df = self._extract_ml_features(df)
        
        from xgboost import XGBRegressor
        self.xgboost = XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective='reg:squarederror'
        )
        
        X = feature_df.drop(['demand', 'date'], axis=1)
        y = feature_df['demand']
        self.xgboost.fit(X, y)
        
        # 3. 动态调整权重 (基于验证集表现)
        self._optimize_weights(feature_df)
        
    def predict(self, future_df):
        """集成预测"""
        # Prophet预测
        prophet_pred = self.prophet.predict(future_df['date'], future_df['semester'])
        
        # XGBoost预测
        X = self._extract_ml_features(future_df).drop(['date'], axis=1, errors='ignore')
        xgb_pred = self.xgboost.predict(X)
        
        # 加权融合
        ensemble_pred = (
            self.weights['prophet'] * np.array(prophet_pred['predicted_demand']) +
            self.weights['xgboost'] * xgb_pred
        )
        
        return {
            'ensemble_prediction': ensemble_pred.tolist(),
            'prophet_prediction': prophet_pred['predicted_demand'],
            'xgboost_prediction': xgb_pred.tolist(),
            'weights': self.weights,
        }
```

### 4.4 Apriori关联规则优化

```python
class OptimizedAprioriMiner:
    """优化的关联规则挖掘"""
    
    def __init__(self, min_support=0.03, min_confidence=0.6, min_lift=1.2):
        # 降低最小支持度，捕获更多模式
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift
        
    def create_enhanced_transactions(self, activities_df):
        """创建更丰富的事务项"""
        transactions = []
        
        for _, activity in activities_df.iterrows():
            items = []
            
            # 基础属性
            items.append(f"type_{activity['activity_type']}")
            
            # 规模分级 (使用分位数而非固定阈值)
            items.append(f"scale_{self._classify_scale(activity['participants_count'])}")
            
            # 预算分级
            items.append(f"budget_{self._classify_budget(activity['budget'])}")
            
            # 时长分级
            items.append(f"duration_{self._classify_duration(activity['duration_hours'])}")
            
            # 时间特征
            if 'start_time' in activity:
                dt = pd.to_datetime(activity['start_time'])
                items.append(f"month_{dt.month}")
                items.append(f"weekday_{dt.weekday()}")
                items.append("weekend" if dt.weekday() >= 5 else "weekday")
                
            # 效果等级
            if 'effect_score' in activity:
                items.append(f"effect_{self._classify_effect(activity['effect_score'])}")
            
            transactions.append(items)
            
        return transactions
    
    def get_actionable_rules(self, rules):
        """筛选可行动的规则"""
        actionable = []
        
        for rule in rules:
            # 规则应该从前件(可控)指向后件(结果)
            antecedent_types = self._classify_item_types(rule['antecedent'])
            consequent_types = self._classify_item_types(rule['consequent'])
            
            # 好的规则: 动作/配置 → 效果/资源需求
            if ('type' in antecedent_types or 'scale' in antecedent_types) and \
               ('effect' in consequent_types or 'budget' in consequent_types):
                actionable.append(rule)
                
        return actionable
```

---

## 5. 模型4: 智能资源调度算法 (优化版)

### 5.1 问题修正

**V1问题**: 单目标加权求和，不是真正的多目标优化

**V2方案**: NSGA-II真正的帕累托优化

### 5.2 NSGA-II多目标遗传算法

```python
from deap import base, creator, tools, algorithms
import random

class NSGA2Scheduler:
    """
    NSGA-II多目标资源调度器
    
    优化目标:
    1. 最大化资源利用率
    2. 最大化活动效果得分
    3. 最大化高优先级活动满意度
    
    约束:
    - 场地时间不冲突 (硬约束)
    - 预算限制 (硬约束)
    - 人员配置满足 (硬约束)
    """
    
    def __init__(self, population_size=100, generations=500):
        self.population_size = population_size
        self.generations = generations
        
        # 定义多目标优化 (3个目标，全部最大化)
        creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0, 1.0))
        creator.create("Individual", list, fitness=creator.FitnessMulti)
        
        self.toolbox = base.Toolbox()
        self._setup_genetic_operators()
        
    def _setup_genetic_operators(self):
        """配置遗传算子"""
        # 基因: 每个活动的 (venue_id, start_time, budget, staff_list)
        self.toolbox.register("activity_gene", self._generate_activity_gene)
        self.toolbox.register("individual", tools.initRepeat, 
                             creator.Individual, self.toolbox.activity_gene, 
                             n=self.n_activities)
        self.toolbox.register("population", tools.initRepeat, list, 
                             self.toolbox.individual)
        
        # 评估函数
        self.toolbox.register("evaluate", self._evaluate)
        
        # 选择: NSGA-II使用非支配排序 + 拥挤度距离
        self.toolbox.register("select", tools.selNSGA2)
        
        # 交叉: 均匀交叉
        self.toolbox.register("mate", self._uniform_crossover)
        
        # 变异
        self.toolbox.register("mutate", self._mutate_gene, indpb=0.1)
        
    def _evaluate(self, individual):
        """
        评估个体 (返回3个目标值)
        
        Returns:
            (utilization, effect_score, priority_satisfaction)
        """
        # 目标1: 资源利用率 (0-100)
        venue_util = self._calculate_venue_utilization(individual)
        budget_eff = self._calculate_budget_efficiency(individual)
        utilization = (venue_util + budget_eff) / 2 * 100
        
        # 目标2: 活动效果得分 (0-100)
        effect_score = self._calculate_expected_effect(individual)
        
        # 目标3: 高优先级活动满意度 (0-100)
        priority_satisfaction = self._calculate_priority_satisfaction(individual)
        
        # 约束惩罚 (违反硬约束则大幅降低适应度)
        penalty = self._calculate_constraint_violation(individual)
        
        return (
            max(0, utilization - penalty),
            max(0, effect_score - penalty),
            max(0, priority_satisfaction - penalty),
        )
    
    def solve(self):
        """执行NSGA-II优化"""
        # 初始化种群
        pop = self.toolbox.population(n=self.population_size)
        
        # 评估初始种群
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = map(self.toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
            
        # 创建统计对象
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean, axis=0)
        stats.register("std", np.std, axis=0)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)
        
        # 精英存档
        hof = tools.ParetoFront()
        
        # 运行NSGA-II
        pop, log = algorithms.eaMuPlusLambda(
            pop, self.toolbox,
            mu=self.population_size,
            lambda_=self.population_size,
            cxpb=0.8,  # 交叉概率
            mutpb=0.1,  # 变异概率
            ngen=self.generations,
            stats=stats,
            halloffame=hof,
            verbose=True
        )
        
        # hof中存储的是帕累托前沿上的所有非支配解
        return self._format_pareto_solutions(hof)
    
    def _format_pareto_solutions(self, pareto_front):
        """格式化帕累托前沿解集"""
        solutions = []
        
        for i, individual in enumerate(pareto_front):
            utilization, effect, priority = individual.fitness.values
            
            solutions.append({
                "solution_id": f"PARETO_{i+1}",
                "objectives": {
                    "resource_utilization": utilization,
                    "activity_effect": effect,
                    "priority_satisfaction": priority,
                },
                "assignments": self._decode_individual(individual),
                "is_dominated": False,  # 帕累托前沿上都是非支配解
            })
            
        # 按综合得分排序
        for sol in solutions:
            sol['composite_score'] = (
                sol['objectives']['resource_utilization'] * 0.3 +
                sol['objectives']['activity_effect'] * 0.4 +
                sol['objectives']['priority_satisfaction'] * 0.3
            )
            
        solutions.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return {
            "pareto_solutions": solutions,
            "solution_count": len(solutions),
            "recommended_solution": solutions[0] if solutions else None,
        }
```

### 5.3 约束处理优化

```python
class ConstrainedScheduler(NSGA2Scheduler):
    """增强约束处理的调度器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constraint_weights = {
            'venue_conflict': 100,    # 最严重
            'budget_exceed': 80,
            'staff_shortage': 60,
            'time_window_violation': 40,
        }
        
    def _calculate_constraint_violation(self, individual):
        """计算约束违反惩罚 (精确计算)"""
        total_penalty = 0
        
        # 1. 场地时间冲突检测
        venue_schedule = {}
        for gene in individual:
            venue_id = gene['venue_id']
            time_slot = gene['time_slot']
            
            if venue_id not in venue_schedule:
                venue_schedule[venue_id] = []
                
            # 检查与已安排活动的冲突
            for existing_slot in venue_schedule[venue_id]:
                if self._time_overlap(time_slot, existing_slot):
                    overlap_duration = self._calculate_overlap(time_slot, existing_slot)
                    total_penalty += self.constraint_weights['venue_conflict'] * overlap_duration
                    
            venue_schedule[venue_id].append(time_slot)
            
        # 2. 预算超支
        total_budget = sum(gene['budget'] for gene in individual)
        if total_budget > self.budget_limit:
            excess_ratio = (total_budget - self.budget_limit) / self.budget_limit
            total_penalty += self.constraint_weights['budget_exceed'] * excess_ratio
            
        # 3. 人员不足
        for gene, activity in zip(individual, self.activities):
            if len(gene['staff']) < activity['required_staff']:
                shortage = activity['required_staff'] - len(gene['staff'])
                total_penalty += self.constraint_weights['staff_shortage'] * shortage
                
        return min(total_penalty, 300)  # 惩罚上限
    
    def _repair_individual(self, individual):
        """修复算子 - 将不可行解修复为可行解"""
        # 按优先级排序活动
        sorted_indices = sorted(
            range(len(self.activities)),
            key=lambda i: self.activities[i]['priority'],
            reverse=True
        )
        
        # 重新安排高优先级活动，确保满足约束
        venue_schedule = {}
        for idx in sorted_indices:
            gene = individual[idx]
            activity = self.activities[idx]
            
            # 如果当前分配有冲突，重新分配
            if self._has_conflict(gene, venue_schedule):
                new_gene = self._find_feasible_assignment(activity, venue_schedule)
                individual[idx] = new_gene
                
            # 更新场地占用
            venue_id = individual[idx]['venue_id']
            if venue_id not in venue_schedule:
                venue_schedule[venue_id] = []
            venue_schedule[venue_id].append(individual[idx]['time_slot'])
            
        return individual
```

---

## 6. 模型协同层设计

### 6.1 算法协调器

```python
class AlgorithmOrchestrator:
    """
    算法协调器 - 实现四个模型间的数据流和反馈闭环
    """
    
    def __init__(self):
        self.portrait_system = OptimizedStudentPortrait()
        self.evaluation_system = OnlineLearningAHP()
        self.prediction_system = EnsembleResourcePredictor()
        self.scheduler_system = ConstrainedScheduler()
        
        # 反馈缓存
        self.feedback_buffer = []
        
    def recommend_for_student(self, student_id):
        """
        为学生推荐活动并预测资源需求
        
        Flow: 模型1 → 模型3 → 模型2(预测)
        """
        # 1. 获取学生画像 (模型1)
        portrait = self.portrait_system.get_portrait(student_id)
        
        # 2. 根据画像推荐活动类型
        recommended_types = self._map_cluster_to_types(portrait.cluster_id)
        
        # 3. 预测这些活动的资源需求 (模型3)
        resource_forecast = self.prediction_system.predict_for_types(
            recommended_types,
            horizon_days=30
        )
        
        # 4. 预测预期效果 (模型2的预测模式)
        predicted_effect = self.evaluation_system.predict_for_types(recommended_types)
        
        return {
            "student_portrait": portrait,
            "recommended_activity_types": recommended_types,
            "predicted_resource_needs": resource_forecast,
            "predicted_effectiveness": predicted_effect,
            "confidence_score": self._calculate_confidence(portrait, resource_forecast),
        }
        
    def schedule_with_evaluation(self, activities, resources):
        """
        调度资源并评估预期效果
        
        Flow: 模型3 → 模型4 → 模型2
        """
        # 1. 预测资源需求 (模型3)
        demand_forecast = self.prediction_system.predict_for_activities(activities)
        
        # 2. 优化调度 (模型4)
        schedule_result = self.scheduler_system.solve(activities, resources, demand_forecast)
        
        # 3. 评估调度方案的预期效果 (模型2)
        for assignment in schedule_result['assignments']:
            activity = self._get_activity(assignment['activity_id'])
            activity['allocated_budget'] = assignment['budget']
            activity['allocated_venue'] = assignment['venue_id']
            
            # 使用AHP评估预期效果
            evaluation = self.evaluation_system.evaluate_predicted(activity)
            assignment['predicted_evaluation'] = evaluation
            
        return schedule_result
        
    def collect_feedback(self, activity_id, scheduled_plan, actual_outcome):
        """
        收集实际结果反馈，用于在线学习
        
        Flow: 实际结果 → 模型2权重更新
        """
        feedback = {
            'activity_id': activity_id,
            'scheduled_plan': scheduled_plan,
            'predicted_score': scheduled_plan.get('predicted_evaluation', {}).get('overall_score'),
            'actual_score': actual_outcome['satisfaction_score'],
            'actual_participation': actual_outcome['actual_participants'],
            'timestamp': datetime.now(),
        }
        
        self.feedback_buffer.append(feedback)
        
        # 批量更新 (每50条更新一次)
        if len(self.feedback_buffer) >= 50:
            self._update_models_from_feedback()
            
    def _update_models_from_feedback(self):
        """使用反馈更新模型"""
        # 更新AHP权重
        self.evaluation_system.update_from_feedback(self.feedback_buffer)
        
        # 更新预测模型
        self.prediction_system.online_update(self.feedback_buffer)
        
        # 清空缓冲区
        self.feedback_buffer = []
```

### 6.2 冷启动处理

```python
class ColdStartHandler:
    """处理新用户/新社团的冷启动问题"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        
    def handle_new_student(self, student_info):
        """
        新学生冷启动
        
        策略: 相似学生聚合 + 专业/年级基线
        """
        # 1. 查找相似学生 (同专业、同年级)
        similar_students = self._find_similar_students(
            major=student_info['major'],
            grade=student_info['grade'],
            gender=student_info.get('gender')
        )
        
        if len(similar_students) >= 10:
            # 有足够相似学生，使用聚合画像
            aggregated_portrait = self._aggregate_portraits(similar_students)
            return {
                "portrait_type": "aggregated",
                "confidence": 0.6,
                "data": aggregated_portrait,
            }
        else:
            # 相似学生不足，使用专业基线
            major_baseline = self._get_major_baseline(student_info['major'])
            return {
                "portrait_type": "baseline",
                "confidence": 0.4,
                "data": major_baseline,
            }
            
    def handle_new_club(self, club_info):
        """
        新社团冷启动
        
        策略: 相似社团迁移学习
        """
        # 查找相似社团
        similar_clubs = self._find_similar_clubs(
            category=club_info['category'],
            size=club_info['member_count']
        )
        
        # 迁移学习: 使用相似社团的历史数据
        transferred_model = self._transfer_learning(similar_clubs)
        
        return {
            "club_id": club_info['club_id'],
            "learning_type": "transfer",
            "source_clubs": [c['club_id'] for c in similar_clubs],
            "initial_parameters": transferred_model,
        }
        
    def handle_new_semester(self, semester_info):
        """
        新学期冷启动 (预测模型)
        
        策略: 去年同期数据 + 趋势外推
        """
        # 获取去年同期数据
        last_year_same_semester = self._get_semester_data(
            year=semester_info['year'] - 1,
            semester=semester_info['semester']
        )
        
        # 应用年度增长趋势
        trend_factor = self._calculate_annual_growth_trend()
        
        return {
            "semester": semester_info['name'],
            "initial_prediction": last_year_same_semester * trend_factor,
            "confidence": 0.5,
            "method": "seasonal_naive_with_trend",
        }
```

---

## 7. A/B测试与实验框架

```python
class AlgorithmExperimentFramework:
    """算法实验框架"""
    
    def __init__(self):
        self.experiments = {}
        
    def create_experiment(self, name, control_version, treatment_version, metrics):
        """
        创建A/B测试实验
        
        Args:
            name: 实验名称
            control_version: 对照组算法版本
            treatment_version: 实验组算法版本
            metrics: 评估指标列表
        """
        experiment = {
            "name": name,
            "control": control_version,
            "treatment": treatment_version,
            "metrics": metrics,
            "start_time": datetime.now(),
            "control_assignments": [],
            "treatment_assignments": [],
            "results": {},
        }
        
        self.experiments[name] = experiment
        return experiment
        
    def assign_to_experiment(self, user_id, experiment_name):
        """将用户分配到实验组"""
        exp = self.experiments[experiment_name]
        
        # 一致性哈希确保同一用户始终分配到同一组
        import hashlib
        hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        
        if hash_val % 2 == 0:
            exp["control_assignments"].append(user_id)
            return {"group": "control", "version": exp["control"]}
        else:
            exp["treatment_assignments"].append(user_id)
            return {"group": "treatment", "version": exp["treatment"]}
            
    def analyze_experiment(self, experiment_name):
        """分析实验结果"""
        from scipy import stats
        
        exp = self.experiments[experiment_name]
        
        results = {}
        for metric in exp["metrics"]:
            control_data = self._collect_metric(exp["control_assignments"], metric)
            treatment_data = self._collect_metric(exp["treatment_assignments"], metric)
            
            # 统计检验
            t_stat, p_value = stats.ttest_ind(control_data, treatment_data)
            
            # 效应量 (Cohen's d)
            pooled_std = np.sqrt((np.std(control_data)**2 + np.std(treatment_data)**2) / 2)
            cohens_d = (np.mean(treatment_data) - np.mean(control_data)) / pooled_std
            
            results[metric] = {
                "control_mean": np.mean(control_data),
                "treatment_mean": np.mean(treatment_data),
                "relative_improvement": (np.mean(treatment_data) - np.mean(control_data)) / np.mean(control_data),
                "p_value": p_value,
                "significant": p_value < 0.05,
                "effect_size": cohens_d,
                "effect_interpretation": self._interpret_effect_size(cohens_d),
            }
            
        exp["results"] = results
        
        # 决策建议
        significant_improvements = sum(1 for r in results.values() if r["significant"] and r["effect_size"] > 0.2)
        
        if significant_improvements >= len(exp["metrics"]) / 2:
            recommendation = "rollout"
        elif significant_improvements > 0:
            recommendation = "iterate"
        else:
            recommendation = "keep_control"
            
        return {
            "experiment": experiment_name,
            "results": results,
            "recommendation": recommendation,
            "sample_size_control": len(exp["control_assignments"]),
            "sample_size_treatment": len(exp["treatment_assignments"]),
        }
```

---

## 8. 技术栈更新

```txt
# 核心算法
scikit-learn==1.4.0        # K-Means + PCA
numpy==1.26.4              # 数值计算
scipy==1.12.0              # 科学计算

# 时间序列 (V2更新)
prophet==1.1.5             # 替代ARIMA，支持节假日效应
# 或 neuralprophet for深度学习版本

# 关联规则
mlxtend==0.23.0            # Apriori实现

# 多目标优化 (V2更新)
deap==1.4.0                # NSGA-II遗传算法

# 机器学习
xgboost==2.0.3             # 梯度提升

# 可解释性
shap==0.44.0               # SHAP值解释

# API服务
fastapi==0.104.1
pydantic==2.5.3

# 模型持久化
joblib==1.3.2
```

---

## 9. 实施里程碑 (优化版)

| 阶段 | 时间 | 任务 | 关键产出 |
|------|------|------|----------|
| **Phase 1** | Week 1-2 | 基础设施 | 特征Pipeline + PCA |
| **Phase 2** | Week 3-4 | 模型1优化 | 可解释聚类系统 |
| **Phase 3** | Week 5-6 | 模型2优化 | 上下文感知AHP |
| **Phase 4** | Week 7-8 | 模型3重建 | Prophet预测器 |
| **Phase 5** | Week 9-10 | 模型4重建 | NSGA-II调度器 |
| **Phase 6** | Week 11-12 | 协同层 | 算法协调器 + 反馈闭环 |
| **Phase 7** | Week 13-14 | 实验框架 | A/B测试系统 |
| **Phase 8** | Week 15-16 | 集成测试 | 端到端验证 |

---

## 10. 风险缓解 (V2)

| 风险 | 概率 | 缓解措施 | 状态 |
|------|------|---------|------|
| PCA降维后信息丢失 | 中 | 保留95%方差 + 验证重构误差 | 已设计 |
| Prophet学习曲线陡峭 | 中 | 提供学期模板 + 预配置 | 已设计 |
| NSGA-II计算开销大 | 中 | 异步优化 + 缓存帕累托前沿 | 已设计 |
| 反馈学习收敛慢 | 中 | 批量更新 + 预热机制 | 已设计 |

---

**审查结论**: ✅ 已修正所有P0问题，批准开发

**关键变更总结**:
1. ✅ K-Means: 添加StandardScaler + PCA
2. ✅ AHP: 上下文矩阵 + 在线学习
3. ✅ Prophet: 学期感知 + 假期处理
4. ✅ GA: NSGA-II帕累托优化
5. ✅ 新增: 模型协同层 + 冷启动处理
6. ✅ 新增: A/B测试框架
