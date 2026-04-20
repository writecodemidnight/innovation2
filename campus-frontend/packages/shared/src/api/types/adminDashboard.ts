/**
 * 管理端仪表盘类型定义
 */

/** 全局统计数据 */
export interface AdminDashboardStats {
  totalClubs: number;
  totalActivities: number;
  totalUsers: number;
  totalParticipants: number;
  ongoingActivities: number;
  pendingActivities: number;
  completedActivities: number;
  todayActivities: number;
  pendingApprovals: number;
  pendingFundApprovals: number;
  totalResources: number;
  occupiedResources: number;
  resourceUtilizationRate: number;
  activityGrowthRate: number;
  participantGrowthRate: number;
}

/** 活动趋势数据 */
export interface ActivityTrend {
  date: string;
  count: number;
}

/** 社团排行数据 */
export interface ClubRanking {
  id: number;
  name: string;
  activityCount: number;
  memberCount: number;
  totalParticipants: number;
  score: number;
}

/** 资源使用情况 */
export interface ResourceUsage {
  typeDistribution: Record<string, number>;
  dailyBookings: Array<{ date: string; count: number }>;
  utilizationRate: number;
}

/** 待办任务统计 */
export interface PendingTasks {
  total: number;
  activityApprovals: number;
  fundApprovals: number;
  resourceBookings: number;
}
