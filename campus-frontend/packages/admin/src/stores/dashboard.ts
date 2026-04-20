import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  apiClient,
  Endpoints,
  type AdminDashboardStats,
  type ActivityTrend,
  type ClubRanking,
  type ResourceUsage,
  type PendingTasks,
} from '@campus/shared';

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const stats = ref<AdminDashboardStats | null>(null);
  const activityTrends = ref<ActivityTrend[]>([]);
  const clubRankings = ref<ClubRanking[]>([]);
  const resourceUsage = ref<ResourceUsage | null>(null);
  const pendingTasks = ref<PendingTasks | null>(null);
  const loading = ref(false);

  // Getters
  const hasData = computed(() => !!stats.value);

  const pendingTotal = computed(() =>
    pendingTasks.value?.total || 0
  );

  // Actions
  const fetchStats = async () => {
    loading.value = true;
    try {
      const data = await apiClient.get<AdminDashboardStats>(
        Endpoints.adminDashboard.stats
      );
      stats.value = data;
      return data;
    } catch (error) {
      console.error('获取统计数据失败:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const fetchActivityTrends = async () => {
    try {
      const data = await apiClient.get<ActivityTrend[]>(
        Endpoints.adminDashboard.activityTrends
      );
      activityTrends.value = data;
      return data;
    } catch (error) {
      console.error('获取活动趋势失败:', error);
      throw error;
    }
  };

  const fetchClubRankings = async () => {
    try {
      const data = await apiClient.get<ClubRanking[]>(
        Endpoints.adminDashboard.clubRankings
      );
      clubRankings.value = data;
      return data;
    } catch (error) {
      console.error('获取社团排行失败:', error);
      throw error;
    }
  };

  const fetchResourceUsage = async () => {
    try {
      const data = await apiClient.get<ResourceUsage>(
        Endpoints.adminDashboard.resourceUsage
      );
      resourceUsage.value = data;
      return data;
    } catch (error) {
      console.error('获取资源使用失败:', error);
      throw error;
    }
  };

  const fetchPendingTasks = async () => {
    try {
      const data = await apiClient.get<PendingTasks>(
        Endpoints.adminDashboard.pendingTasks
      );
      pendingTasks.value = data;
      return data;
    } catch (error) {
      console.error('获取待办任务失败:', error);
      throw error;
    }
  };

  // 加载所有Dashboard数据
  const loadAllDashboardData = async () => {
    loading.value = true;
    try {
      await Promise.all([
        fetchStats(),
        fetchActivityTrends(),
        fetchClubRankings(),
        fetchResourceUsage(),
        fetchPendingTasks(),
      ]);
    } finally {
      loading.value = false;
    }
  };

  return {
    stats,
    activityTrends,
    clubRankings,
    resourceUsage,
    pendingTasks,
    loading,
    hasData,
    pendingTotal,
    fetchStats,
    fetchActivityTrends,
    fetchClubRankings,
    fetchResourceUsage,
    fetchPendingTasks,
    loadAllDashboardData,
  };
});
