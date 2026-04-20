import { apiClient } from '@campus/shared';
import type { ClubDashboardStats } from '@campus/shared';

export const dashboardApi = {
  /** 获取社团仪表盘统计数据 */
  getStats: () => apiClient.get<ClubDashboardStats>('/api/v1/dashboard/stats'),
};
