"""
智能数据生成模块使用演示
============================
展示如何使用 campus-ai/src/data/mock/ 生成逼真的校园数据
"""

import sys
sys.path.insert(0, 'src')

# ============================================================
# 1. 最简用法 - 一键生成完整数据集
# ============================================================
print("=" * 60)
print("演示 1: 一键生成完整数据集")
print("=" * 60)

from data.mock.smart_data_generator import generate_smart_dataset

data = generate_smart_dataset(
    student_count=100,      # 100个学生
    club_count=5,           # 5个社团
    activity_count=20,      # 20个活动
    seed=42                 # 固定种子，可复现
)

print(f"[成功] 生成完成!")
print(f"  - 学生数: {len(data['students'])}")
print(f"  - 社团数: {len(data['clubs'])}")
print(f"  - 活动数: {len(data['activities'])}")
print(f"  - 参与记录: {len(data['participation'])}")
print(f"  - 质量评分: {data['quality_after'].overall_score:.1f}/100")

# 查看前几行数据
print("\n学生数据样例:")
print(data['students'].head(3)[['student_id', 'name', 'persona', 'major']].to_string())

print("\n社团数据样例:")
print(data['clubs'].head(3)[['club_id', 'club_name', 'club_type']].to_string())

print("\n活动数据样例:")
print(data['activities'].head(3)[['activity_name', 'start_time', 'club_id']].to_string())


# ============================================================
# 2. 高级用法 - 注入资源冲突（用于测试GA算法）
# ============================================================
print("\n" + "=" * 60)
print("演示 2: 生成带资源冲突的数据（GA算法测试）")
print("=" * 60)

from data.mock.smart_data_generator import SmartDataGenerator

generator = SmartDataGenerator(seed=42)
result = generator.generate_full_dataset(
    student_count=50,
    club_count=3,
    activity_count=50,          # 更多活动以制造冲突
    inject_conflicts=True,      # 注入资源冲突
    inject_dirty_data=False     # 不注入脏数据
)

activities = result['activities']
conflicts = activities[activities['resource_conflict'] == True]

print(f"[成功] 生成了 {len(activities)} 个活动")
print(f"  - 其中 {len(conflicts)} 个活动存在资源冲突")

if len(conflicts) > 0:
    print(f"\n冲突活动示例:")
    print(conflicts[['activity_name', 'start_time', 'resource_type', 'conflict_severity']].head().to_string())


# ============================================================
# 3. 高级用法 - 注入脏数据（测试清洗流程）
# ============================================================
print("\n" + "=" * 60)
print("演示 3: 生成带脏数据的数据集（左右互搏测试）")
print("=" * 60)

generator2 = SmartDataGenerator(seed=42)
result2 = generator2.generate_full_dataset(
    student_count=100,
    club_count=5,
    activity_count=20,
    inject_conflicts=False,
    inject_dirty_data=True      # 注入5%脏数据
)

print(f"[成功] 质量评分对比:")
print(f"  - 清洗前: {result2['quality_before'].overall_score:.1f}/100")
print(f"  - 清洗后: {result2['quality_after'].overall_score:.1f}/100")
print(f"  - 提升: +{result2['quality_after'].overall_score - result2['quality_before'].overall_score:.1f}分")

# 查看生成报告
print(f"\n生成报告:")
print(generator2.get_generation_report())


# ============================================================
# 4. 单独使用模块
# ============================================================
print("\n" + "=" * 60)
print("演示 4: 单独使用各模块")
print("=" * 60)

# 4.1 角色生成器
print("\n4.1 角色模板系统:")
from data.mock.personas import generate_mock_students

students = generate_mock_students(count=10, seed=42)
print(f"生成了 {len(students)} 个学生")
print("角色分布:")
print(students['persona'].value_counts().to_string())

# 4.2 校园时间规律
print("\n4.2 校园时间规律:")
from data.mock.campus_rhythm import generate_campus_activity_times

times = generate_campus_activity_times(count=20, seed=42)
weekend_count = sum(1 for start, end in times if start.weekday() in [5, 6])
print(f"生成了 {len(times)} 个活动时间")
print(f"其中 {weekend_count} 个在周末 ({weekend_count/len(times)*100:.0f}%)")

# 4.3 资源冲突注入
print("\n4.3 资源冲突注入:")
import pandas as pd
from datetime import datetime, timedelta
from data.mock.conflict_injector import inject_resource_conflicts

# 创建周五下午的活动（高冲突时段）
activities_df = pd.DataFrame({
    'activity_id': [f'ACT{i:03d}' for i in range(15)],
    'start_time': pd.date_range('2024-03-15 15:00', periods=15, freq='15min'),  # 周五下午
    'activity_type': ['lecture'] * 15,
    'participant_count': [50] * 15
})

conflict_df = inject_resource_conflicts(activities_df, intensity=2.0, seed=42)
conflict_count = conflict_df['resource_conflict'].sum()
print(f"在周五下午安排了 15 个活动")
print(f"检测到 {conflict_count} 个资源冲突")
print(f"最高严重等级: {conflict_df['conflict_severity'].max()}")

# 4.4 脏数据注入
print("\n4.4 脏数据注入:")
from data.mock.dirty_data_injector import inject_dirty_data

clean_df = pd.DataFrame({
    'id': range(100),
    'name': [f'活动{i}' for i in range(100)],
    'value': range(100)
})

dirty_df = inject_dirty_data(clean_df, dirty_ratio=0.05, seed=42)
null_count = dirty_df.isnull().sum().sum()
print(f"原始数据: 100 条干净记录")
print(f"注入后: {null_count} 个缺失值")
print(f"污染率: {null_count/100*100:.1f}%")


# ============================================================
# 5. 数据导出
# ============================================================
print("\n" + "=" * 60)
print("演示 5: 导出数据到CSV")
print("=" * 60)

import os

# 创建输出目录
output_dir = './demo_output'
os.makedirs(output_dir, exist_ok=True)

# 导出所有表
data['students'].to_csv(f'{output_dir}/students.csv', index=False, encoding='utf-8-sig')
data['clubs'].to_csv(f'{output_dir}/clubs.csv', index=False, encoding='utf-8-sig')
data['activities'].to_csv(f'{output_dir}/activities.csv', index=False, encoding='utf-8-sig')
data['participation'].to_csv(f'{output_dir}/participation.csv', index=False, encoding='utf-8-sig')

print(f"[成功] 数据已导出到 {output_dir}/")
print(f"  - students.csv ({os.path.getsize(f'{output_dir}/students.csv')/1024:.1f} KB)")
print(f"  - clubs.csv ({os.path.getsize(f'{output_dir}/clubs.csv')/1024:.1f} KB)")
print(f"  - activities.csv ({os.path.getsize(f'{output_dir}/activities.csv')/1024:.1f} KB)")
print(f"  - participation.csv ({os.path.getsize(f'{output_dir}/participation.csv')/1024:.1f} KB)")


# ============================================================
# 6. 数据分析示例
# ============================================================
print("\n" + "=" * 60)
print("演示 6: 简单的数据分析")
print("=" * 60)

# 角色与社团类型的关联
print("\n角色-社团偏好分析:")
students = data['students']
participation = data['participation']
activities = data['activities'][['activity_id', 'club_id']]
clubs = data['clubs'][['club_id', 'club_type']]

# 合并数据
merged = participation.merge(students, on='student_id')
merged = merged.merge(activities, on='activity_id')
merged = merged.merge(clubs, on='club_id')

# 统计各角色偏好的社团类型
persona_club = merged.groupby(['persona', 'club_type']).size().unstack(fill_value=0)
print(persona_club.to_string())

# 活动时间分布
print("\n活动时间分布:")
activities = data['activities']
activities['hour'] = pd.to_datetime(activities['start_time']).dt.hour
hour_dist = activities['hour'].value_counts().sort_index()
print(hour_dist.head(10).to_string())


print("\n" + "=" * 60)
print("演示完成! 所有功能正常运行 [成功]")
print("=" * 60)
print("\n使用建议:")
print("1. 小规模测试: generate_smart_dataset(100, 5, 20)")
print("2. GA算法测试: inject_conflicts=True")
print("3. 清洗流程测试: inject_dirty_data=True")
print("4. 固定种子(seed)可以确保结果可复现")
