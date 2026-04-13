#!/usr/bin/env python3
"""
智能数据生成器 CLI 工具

Usage:
    python cli.py generate --students 1000 --clubs 20 --activities 200
    python cli.py generate --small  # 快速生成小规模测试数据
    python cli.py report --input-dir ./data
    python cli.py validate --activities activities.csv
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.mock.smart_data_generator import SmartDataGenerator
from data.mock.personas import PersonaGenerator
from data.mock.campus_rhythm import CampusRhythmGenerator
import pandas as pd

# 尝试导入数据管道模块（如果不可用则跳过）
try:
    from data.quality import DataQualityChecker
    from data.transformers.cleaner import DataCleaner
    HAS_DATA_PIPELINE = True
except ImportError:
    HAS_DATA_PIPELINE = False


def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_stat(label: str, value, indent: int = 0):
    """打印统计项"""
    prefix = "  " * indent
    print(f"{prefix}{label:<25} {value}")


def cmd_generate(args):
    """生成数据命令"""
    print_header("智能数据生成器")

    # 确定规模
    if args.small:
        student_count, club_count, activity_count = 100, 5, 20
    elif args.medium:
        student_count, club_count, activity_count = 500, 10, 100
    elif args.large:
        student_count, club_count, activity_count = 5000, 50, 1000
    else:
        student_count = args.students
        club_count = args.clubs
        activity_count = args.activities

    print(f"\n[数据] 生成规模:")
    print_stat("学生数量", f"{student_count} 人")
    print_stat("社团数量", f"{club_count} 个")
    print_stat("活动数量", f"{activity_count} 场")
    print_stat("随机种子", args.seed)

    # 创建生成器
    generator = SmartDataGenerator(seed=args.seed)

    # 生成数据
    result = generator.generate_full_dataset(
        student_count=student_count,
        club_count=club_count,
        activity_count=activity_count,
        inject_conflicts=not args.no_conflicts,
        inject_dirty_data=not args.no_dirty,
        dirty_data_ratio=args.dirty_ratio,
        output_dir=args.output
    )

    # 打印报告
    print("\n" + generator.get_generation_report())

    return 0


def cmd_report(args):
    """生成报告命令"""
    print_header("数据分析报告")

    input_dir = Path(args.input_dir)

    # 加载数据
    try:
        students = pd.read_csv(input_dir / "students.csv")
        clubs = pd.read_csv(input_dir / "clubs.csv")
        activities = pd.read_csv(input_dir / "activities.csv")
        participation = pd.read_csv(input_dir / "participation.csv")
    except FileNotFoundError as e:
        print(f"[错误] 文件未找到: {e}")
        return 1

    print(f"\n[文件] 数据目录: {input_dir}")

    # 基础统计
    print("\n[数据] 基础统计:")
    print_stat("学生总数", f"{len(students)} 人")
    print_stat("社团总数", f"{len(clubs)} 个")
    print_stat("活动总数", f"{len(activities)} 场")
    print_stat("参与记录", f"{len(participation)} 条")

    # 角色分布
    if 'persona' in students.columns:
        print("\n[用户] 学生角色分布:")
        for persona, count in students['persona'].value_counts().items():
            pct = count / len(students) * 100
            print_stat(f"  {persona}", f"{count} ({pct:.1f}%)", indent=1)

    # 活动时间分布
    if 'is_weekend' in activities.columns:
        print("\n[日期] 活动时间分布:")
        weekend_count = activities['is_weekend'].sum()
        weekday_count = len(activities) - weekend_count
        print_stat("  周末活动", f"{weekend_count} ({weekend_count/len(activities)*100:.1f}%)", indent=1)
        print_stat("  工作日活动", f"{weekday_count} ({weekday_count/len(activities)*100:.1f}%)", indent=1)

    # 冲突统计
    if 'resource_conflict' in activities.columns:
        conflict_count = activities['resource_conflict'].sum()
        print("\n[冲突] 资源冲突:")
        print_stat("  冲突活动数", f"{conflict_count}", indent=1)
        print_stat("  冲突率", f"{conflict_count/len(activities)*100:.1f}%", indent=1)

    # 质量检查
    if HAS_DATA_PIPELINE:
        print("\n[检查] 数据质量:")
        checker = DataQualityChecker()
        report = checker.check(activities, "activities")
        print_stat("  总体评分", f"{report.overall_score:.1f}/100", indent=1)
        print_stat("  完整性", f"{report.completeness:.1f}%", indent=1)
        print_stat("  一致性", f"{report.consistency:.1f}%", indent=1)
    else:
        print("\n[检查] 数据质量检查需要安装数据管道模块")

    return 0


def cmd_validate(args):
    """验证数据质量命令"""
    print_header("数据质量验证")

    if not HAS_DATA_PIPELINE:
        print("\n[警告]  数据质量检查需要安装数据管道模块")
        return 1

    # 加载数据
    try:
        df = pd.read_csv(args.file)
    except FileNotFoundError:
        print(f"[错误] 文件未找到: {args.file}")
        return 1

    print(f"\n[文件] 验证文件: {args.file}")
    print(f"[数据] 记录数: {len(df)}")

    # 质量检查
    checker = DataQualityChecker()
    report = checker.check(df, Path(args.file).stem)

    print("\n[报告] 质量报告:")
    print_stat("总体评分", f"{report.overall_score:.1f}/100")
    print_stat("质量等级", checker.get_quality_level(report.overall_score))
    print_stat("完整性", f"{report.completeness:.1f}%")
    print_stat("准确性", f"{report.accuracy:.1f}%")
    print_stat("一致性", f"{report.consistency:.1f}%")
    print_stat("有效性", f"{report.validity:.1f}%")

    # 详细建议
    print("\n[建议] 建议:")
    recommendations = checker._get_recommendations(report)
    for line in recommendations.split('\n'):
        if line.strip():
            print(f"  {line}")

    # 如果质量低于阈值，返回错误码
    if report.overall_score < args.threshold:
        print(f"\n[警告]  质量评分低于阈值 {args.threshold}")
        return 1

    print("\n[完成] 数据质量验证通过")
    return 0


def cmd_insights(args):
    """生成数据洞察命令"""
    print_header("数据洞察分析")

    input_dir = Path(args.input_dir)

    # 加载数据
    try:
        students = pd.read_csv(input_dir / "students.csv")
        clubs = pd.read_csv(input_dir / "clubs.csv")
        activities = pd.read_csv(input_dir / "activities.csv")
        participation = pd.read_csv(input_dir / "participation.csv")
    except FileNotFoundError as e:
        print(f"[错误] 文件未找到: {e}")
        return 1

    print("\n[检查] 深度洞察:")

    # 1. 最活跃社团
    print("\n[TOP] 最活跃社团 TOP 5:")
    activity_counts = activities.groupby('club_id').size().sort_values(ascending=False).head(5)
    for club_id, count in activity_counts.items():
        club_name = clubs[clubs['club_id'] == club_id]['club_name'].values[0]
        print(f"  {club_name}: {count} 场活动")

    # 2. 最受欢迎活动类型
    if 'activity_type' in activities.columns:
        print("\n[类型] 活动类型分布:")
        type_dist = activities['activity_type'].value_counts().head(5)
        for act_type, count in type_dist.items():
            print(f"  {act_type}: {count} 场")

    # 3. 学生参与度
    if 'student_id' in participation.columns:
        print("\n[人数] 学生参与度:")
        participation_count = participation.groupby('student_id').size()
        print_stat("平均每人参与", f"{participation_count.mean():.1f} 场")
        print_stat("最多参与", f"{participation_count.max()} 场")
        print_stat("最少参与", f"{participation_count.min()} 场")

    # 4. 活动满意度
    if 'rating' in participation.columns:
        print("\n[评分] 活动满意度:")
        avg_rating = participation['rating'].mean()
        print_stat("平均评分", f"{avg_rating:.2f}/5")
        rating_dist = participation['rating'].value_counts().sort_index()
        for rating, count in rating_dist.items():
            pct = count / len(participation) * 100
            bar = "█" * int(pct / 5)
            print(f"  {rating}分: {bar} {count} ({pct:.1f}%)")

    # 5. 时间模式
    if 'time_slot' in activities.columns:
        print("\n[时段] 时段偏好:")
        slot_dist = activities['time_slot'].value_counts()
        for slot, count in slot_dist.items():
            print(f"  {slot}: {count} 场")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="智能数据生成器 - 生成比真的还真的数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成小规模测试数据
  python cli.py generate --small --output ./test_data

  # 生成指定规模数据
  python cli.py generate -s 1000 -c 20 -a 200 --seed 42

  # 查看数据报告
  python cli.py report --input-dir ./data

  # 数据质量验证
  python cli.py validate --file activities.csv --threshold 80

  # 深度洞察
  python cli.py insights --input-dir ./data
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # generate 命令
    gen_parser = subparsers.add_parser('generate', help='生成模拟数据')
    gen_parser.add_argument('-s', '--students', type=int, default=1000, help='学生数量')
    gen_parser.add_argument('-c', '--clubs', type=int, default=20, help='社团数量')
    gen_parser.add_argument('-a', '--activities', type=int, default=200, help='活动数量')
    gen_parser.add_argument('--seed', type=int, default=42, help='随机种子')
    gen_parser.add_argument('-o', '--output', default='./smart_data', help='输出目录')
    gen_parser.add_argument('--small', action='store_true', help='小规模(100/5/20)')
    gen_parser.add_argument('--medium', action='store_true', help='中规模(500/10/100)')
    gen_parser.add_argument('--large', action='store_true', help='大规模(5000/50/1000)')
    gen_parser.add_argument('--no-conflicts', action='store_true', help='不注入资源冲突')
    gen_parser.add_argument('--no-dirty', action='store_true', help='不注入脏数据')
    gen_parser.add_argument('--dirty-ratio', type=float, default=0.05, help='脏数据比例')
    gen_parser.set_defaults(func=cmd_generate)

    # report 命令
    report_parser = subparsers.add_parser('report', help='生成数据报告')
    report_parser.add_argument('-i', '--input-dir', required=True, help='数据目录')
    report_parser.set_defaults(func=cmd_report)

    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='验证数据质量')
    validate_parser.add_argument('-f', '--file', required=True, help='CSV文件路径')
    validate_parser.add_argument('-t', '--threshold', type=float, default=60, help='质量阈值')
    validate_parser.set_defaults(func=cmd_validate)

    # insights 命令
    insights_parser = subparsers.add_parser('insights', help='生成数据洞察')
    insights_parser.add_argument('-i', '--input-dir', required=True, help='数据目录')
    insights_parser.set_defaults(func=cmd_insights)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
