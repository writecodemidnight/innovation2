# 智能数据生成模块 (Smart Mock Data Generator)

## 概述

这是一个专门为校园社团活动评估系统设计的智能数据生成模块。生成的数据"比真的还真"，因为它遵循真实世界的规律和约束。

## 核心特性

### 1. 角色模板系统 (Persona-Based Generation)

不是随机分配标签，而是基于"角色模板"生成学生：

| 角色 | 特点 | 社团偏好 |
|-----|------|---------|
| **TechGeek** | 男性75%，CS专业为主 | 科技类80% |
| **Artist** | 女性45%，人文专业 | 文艺类85% |
| **Athlete** | 男性60%，体育/工科 | 体育类90% |
| **Socializer** | 均衡，商科/文科 | 公益/社交类 |
| **Scholar** | 均衡，理科专业 | 学术类80% |
| **Casual** | 随缘，各专业的低参与度者 | 随机 |

**为什么重要**：K-Means聚类算法能找到真实的群体结构，而不是随机噪声。

### 2. 校园时间规律 (Campus Rhythm)

活动时间符合真实校园节奏：

- **月份分布**：避开1-2月、7-8月（寒暑假）
- **周分布**：周五(18%)、周六(25%)、周日(15%)活动最多
- **日分布**：下午(14-17点)、晚上(19-21点)最受欢迎
- **考试周**：6月和12月中旬活动接近0

**为什么重要**：LSTM时间序列模型能学到真实的周期性规律。

### 3. 资源冲突注入 (Conflict Injection)

故意制造资源短缺，测试GA遗传算法：

| 冲突场景 | 描述 | 资源/需求比 |
|---------|------|------------|
| **周五下午** | 10个活动抢3个多媒体教室 | 1:3.5 |
| **周六体育馆** | 全天爆满，场地严重不足 | 1:4.0 |
| **社团招新周** | 开学季场地争抢 | 1:2.5 |
| **期末晚会** | 礼堂供不应求 | 1:3.0 |

**为什么重要**：测试GA算法在高压情况下的冲突解决能力。

### 4. 脏数据注入 (Dirty Data Injection)

故意污染5%的数据，测试DataCleaner：

| 污染类型 | 比例 | 示例 |
|---------|------|------|
| 缺失值 | 2% | participant_count = NULL |
| 异常值 | 1.5% | budget = -1000 或 9999999 |
| 不一致 | 1% | end_time < start_time |
| 拼写错误 | 0.5% | "社团活动" → "社団活動" |

**为什么重要**：验证数据清洗流程是否真的有效。

### 5. 质量自验证 (Quality Self-Check)

生成后立即进行"左右互搏"：

```
DataGenerator → 脏数据 → DataCleaner → 干净数据
     ↑                                      ↓
   质量评分                              质量评分
    60分                                  95分
                ↑ 提升 35分 ✓
```

## 快速开始

### 命令行使用

```bash
# 生成小规模测试数据
python -m data.mock.cli generate --small --output ./test_data

# 生成指定规模数据
python -m data.mock.cli generate -s 1000 -c 20 -a 200 --seed 42

# 查看数据报告
python -m data.mock.cli report --input-dir ./test_data

# 验证数据质量
python -m data.mock.cli validate --file activities.csv
```

### Python API

```python
from data.mock.smart_data_generator import SmartDataGenerator

# 创建生成器
generator = SmartDataGenerator(seed=42)

# 生成完整数据集
result = generator.generate_full_dataset(
    student_count=1000,
    club_count=20,
    activity_count=200,
    inject_conflicts=True,    # 注入资源冲突
    inject_dirty_data=True,   # 注入脏数据
    output_dir='./data'
)

# 获取各表数据
students = result['students']
clubs = result['clubs']
activities = result['activities']
participation = result['participation']

# 查看生成报告
print(generator.get_generation_report())
```

### 便捷函数

```python
from data.mock.smart_data_generator import generate_smart_dataset

# 一键生成
data = generate_smart_dataset(
    student_count=1000,
    club_count=20,
    activity_count=200,
    seed=42
)

print(data['generation_stats'])
```

## 数据表结构

### students (学生表)
```python
{
    'student_id': '24CS0001',      # 学号：年份+专业+序号
    'name': '张三',
    'gender': 'M',
    'enrollment_year': 2024,
    'grade_level': 1,
    'major': 'CS',
    'persona': 'tech_geek',        # 角色标签
    'interest_tags': 'tech,academic',
    'activity_frequency': 'high',
    'feedback_style': 'critical',
    'email': '24CS0001@campus.edu.cn',
    'phone': '13800138000'
}
```

### clubs (社团表)
```python
{
    'club_id': 'CLUB1000',
    'club_name': '机器人社',
    'club_type': 'tech',           # tech/arts/sports/academic/public
    'club_type_name': '科技类',
    'founding_year': 2018,
    'member_count': 85,
    'rating': 4,                   # 1-5星
    'advisor_name': '李老师',
    'contact_email': 'club1000@campus.edu.cn',
    'status': 'active'
}
```

### activities (活动表)
```python
{
    'activity_id': 'ACT10000',
    'club_id': 'CLUB1000',
    'activity_name': '讲座-12',
    'activity_type': '讲座',
    'start_time': '2024-03-15 15:00:00',
    'end_time': '2024-03-15 17:00:00',
    'participant_count': 50,
    'max_capacity': 65,
    'budget_amount': 3500,
    'location': '场地-23',
    'status': 'completed',
    # 时间特征
    'is_weekend': False,
    'is_exam_period': False,
    'semester': 'spring',
    'time_slot': 'afternoon',
    # 资源冲突标记
    'resource_type': 'multimedia_room',
    'resource_id': 'multimedia_room_0',
    'resource_conflict': True,
    'conflict_severity': 7
}
```

### participation (参与记录表)
```python
{
    'participation_id': 'PART0000001',
    'activity_id': 'ACT10000',
    'student_id': '24CS0001',
    'registration_time': '2024-03-08 10:00:00',
    'check_in_time': '2024-03-15 14:58:00',
    'check_out_time': '2024-03-15 17:05:00',
    'rating': 4,                   # 1-5分评价
    'feedback': '活动还不错',
    'status': 'attended'
}
```

## 模块架构

```
data/mock/
├── __init__.py                  # 模块导出
├── personas.py                  # 角色模板系统
│   ├── StudentPersona          # 角色定义
│   ├── PersonaGenerator        # 角色生成器
│   └── generate_mock_students  # 便捷函数
├── campus_rhythm.py             # 校园时间规律
│   ├── CampusRhythmGenerator   # 时间生成器
│   └── generate_campus_activity_times  # 便捷函数
├── conflict_injector.py         # 资源冲突注入
│   ├── ConflictInjector        # 冲突注入器
│   ├── ResourceSchedulerTestCase  # GA测试用例
│   └── inject_resource_conflicts  # 便捷函数
├── dirty_data_injector.py       # 脏数据注入
│   ├── DirtyDataInjector       # 脏数据注入器
│   └── inject_dirty_data       # 便捷函数
├── smart_data_generator.py      # 智能数据生成器
│   ├── SmartDataGenerator      # 主生成器
│   └── generate_smart_dataset  # 便捷函数
├── cli.py                       # 命令行工具
└── README.md                    # 本文档
```

## 测试

```bash
# 运行所有mock模块测试
python -m pytest tests/data/mock/ -v

# 运行特定测试
python -m pytest tests/data/mock/test_smart_generator.py -v
```

## 使用场景

### 1. 算法模型训练
```python
# 为K-Means聚类生成数据
data = generate_smart_dataset(5000, 50, 1000)
students = data['students']
# students['persona'] 提供了真实的标签用于验证聚类效果
```

### 2. 推荐系统冷启动
```python
# 生成历史数据训练推荐模型
data = generate_smart_dataset(10000, 100, 5000)
# 基于persona的活动偏好可以验证推荐准确性
```

### 3. 资源调度算法测试
```python
# 注入冲突测试GA算法
generator = SmartDataGenerator(seed=42)
result = generator.generate_full_dataset(
    activity_count=200,
    inject_conflicts=True,  # 制造资源冲突
    inject_dirty_data=False
)
activities = result['activities']
# 使用resource_conflict标记验证GA解决效果
```

### 4. 数据清洗流程验证
```python
# 左右互搏测试
generator = SmartDataGenerator(seed=42)
result = generator.generate_full_dataset(
    inject_dirty_data=True,  # 注入脏数据
)
# result['quality_before'] 和 result['quality_after'] 对比
```

## 注意事项

1. **种子一致性**：使用相同的seed可以得到完全相同的数据，便于复现实验
2. **外键一致性**：所有关联数据（student_id, club_id, activity_id）都保持正确的引用关系
3. **性能考虑**：生成10000+数据可能需要几秒钟，建议分批生成
4. **存储空间**：完整数据集（5000学生/50社团/1000活动）约占用10MB CSV空间

## 扩展开发

### 添加新角色
```python
# 在 personas.py 中添加
personas['new_role'] = StudentPersona(
    persona_id='new_role',
    name='新角色',
    description='描述',
    gender_ratio=0.5,
    major_weights={'CS': 0.5, 'ART': 0.5},
    club_preferences=[
        ClubPreference('tech', 0.7, 'high', (1000, 5000))
    ]
)
```

### 添加新冲突场景
```python
# 在 conflict_injector.py 中添加
CONFLICT_SCENARIOS['new_scenario'] = {
    'description': '新冲突场景',
    'time_filter': lambda dt: dt.weekday() == 0,  # 周一
    'resource_type': 'new_resource',
    'resource_count': 2,
    'demand_multiplier': 3.0,
}
```

## 性能基准

| 数据规模 | 生成时间 | 内存占用 |
|---------|---------|---------|
| 100学生/5社团/20活动 | 0.5s | ~10MB |
| 1000学生/20社团/200活动 | 2s | ~50MB |
| 5000学生/50社团/1000活动 | 8s | ~200MB |
| 10000学生/100社团/5000活动 | 30s | ~800MB |

## 许可证

MIT License - 用于校园社团活动评估系统
