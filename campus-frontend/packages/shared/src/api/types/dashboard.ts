/**
 * 仪表盘统计类型定义
 */

/** 社团仪表盘统计数据 */
export interface ClubDashboardStats {
  /** 本月活动数 */
  monthlyActivities: number;

  /** 本月活动增长率 */
  monthlyGrowthRate: number;

  /** 参与人次 */
  totalParticipants: number;

  /** 平均评分 */
  averageRating: number;

  /** 资源利用率 */
  resourceUtilizationRate: number;

  /** 待审批申请数 */
  pendingApprovals: number;

  /** 进行中活动数 */
  ongoingActivities: number;

  /** 已结束活动数 */
  completedActivities: number;
}

/** 活动趋势数据 */
export interface ActivityTrend {
  /** 日期列表 */
  dates: string[];
  /** 每天的活动数量 */
  counts: number[];
}

/** 活动类型分布项 */
export interface ActivityTypeItem {
  /** 类型名称 */
  name: string;
  /** 类型编码 */
  code: string;
  /** 活动数量 */
  value: number;
}

/** 活动类型分布 */
export interface ActivityTypeDistribution {
  /** 类型分布列表 */
  types: ActivityTypeItem[];
}
