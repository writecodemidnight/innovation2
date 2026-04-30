import { apiClient } from '@campus/shared/api/client.axios';
import type { ClubDashboardStats, ActivityTrend, ActivityTypeDistribution } from '@campus/shared';

export const dashboardApi = {
  /** 获取社团仪表盘统计数据 */
  getStats: () => apiClient.get<ClubDashboardStats>('/api/v1/dashboard/stats'),

  /** 获取活动趋势数据 */
  getActivityTrends: (start: string, end: string) =>
    apiClient.get<ActivityTrend>('/api/v1/dashboard/activity-trends', { params: { start, end } }),

  /** 获取活动类型分布 */
  getActivityTypeDistribution: () =>
    apiClient.get<ActivityTypeDistribution>('/api/v1/dashboard/activity-types'),
};
