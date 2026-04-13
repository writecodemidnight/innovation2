/**
 * 评估相关类型定义
 */

/** 评估维度 */
export enum EvaluationDimension {
  PARTICIPATION = 'PARTICIPATION',
  EDUCATIONAL = 'EDUCATIONAL',
  INNOVATION = 'INNOVATION',
  INFLUENCE = 'INFLUENCE',
  SUSTAINABILITY = 'SUSTAINABILITY'
}

/** 活动评估结果 */
export interface EvaluationResult {
  activityId: number;
  dimensions: {
    [EvaluationDimension.PARTICIPATION]: number;
    [EvaluationDimension.EDUCATIONAL]: number;
    [EvaluationDimension.INNOVATION]: number;
    [EvaluationDimension.INFLUENCE]: number;
    [EvaluationDimension.SUSTAINABILITY]: number;
  };
  compositeScore: number;
  ranking?: number;
  percentile?: number;
}

/** 全局统计数据 */
export interface GlobalStatistics {
  totalActivities: number;
  totalParticipants: number;
  activeClubs: number;
  avgSatisfaction: number;
  monthlyGrowth: number;
  recentActivities: number;
  pendingApprovals: number;
  resourceUtilization: number;
}

/** 趋势数据 */
export interface TrendData {
  date: string;
  value: number;
}

/** 仪表盘数据 */
export interface DashboardData {
  statistics: GlobalStatistics;
  activityTrend: TrendData[];
  participationTrend: TrendData[];
  categoryDistribution: { name: string; value: number }[];
  topClubs: { id: number; name: string; score: number }[];
  alerts: DashboardAlert[];
}

/** 仪表盘告警 */
export interface DashboardAlert {
  id: number;
  type: 'INFO' | 'WARNING' | 'ERROR';
  title: string;
  message: string;
  createdAt: string;
  isRead: boolean;
}

/** 资源优化建议 */
export interface ResourceOptimizationSuggestion {
  id: number;
  resourceType: string;
  currentAllocation: number;
  suggestedAllocation: number;
  reason: string;
  expectedImprovement: string;
  confidence: number;
}

/** 智能调度结果 */
export interface SchedulingResult {
  originalSchedule: { activityId: number; startTime: string; endTime: string }[];
  optimizedSchedule: { activityId: number; startTime: string; endTime: string; resourceId?: number }[];
  conflictsResolved: number;
  resourceUtilizationImprovement: number;
  explanation: string;
}
