import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  apiClient,
  Endpoints,
  type ApprovalCounts,
  type HistoryCounts,
  type ApprovalRequest,
  type Activity,
  type ResourceBooking,
  type FundApplication,
  type PageResponse,
} from '@campus/shared';

export const useApprovalStore = defineStore('approval', () => {
  // State
  const approvalCounts = ref<ApprovalCounts | null>(null);
  const historyCounts = ref<HistoryCounts | null>(null);
  const pendingActivities = ref<Activity[]>([]);
  const pendingResourceBookings = ref<ResourceBooking[]>([]);
  const pendingFundApplications = ref<FundApplication[]>([]);
  const loading = ref(false);

  // Getters
  const totalPending = computed(() => {
    if (!approvalCounts.value) return 0;
    return (approvalCounts.value.activities || 0) +
           (approvalCounts.value.resourceBookings || 0) +
           (approvalCounts.value.fundApplications || 0);
  });

  // Actions - 待审批统计
  const fetchApprovalCounts = async () => {
    try {
      const data = await apiClient.get<ApprovalCounts>(
        Endpoints.adminApprovals.counts
      );
      approvalCounts.value = data;
      return data;
    } catch (error) {
      console.error('获取待审批统计失败:', error);
      throw error;
    }
  };

  // Actions - 待审批活动
  const fetchPendingActivities = async (page = 0, size = 10) => {
    loading.value = true;
    try {
      const data = await apiClient.get<Activity[]>(
        Endpoints.adminApprovals.pendingActivities,
        { params: { page, size } }
      );
      pendingActivities.value = data;
      return data;
    } catch (error) {
      console.error('获取待审批活动失败:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const approveActivity = async (id: number, comment?: string) => {
    try {
      const request: ApprovalRequest = { comment };
      const response = await apiClient.post(
        Endpoints.adminApprovals.approveActivity(id),
        request
      );
      // 刷新列表
      await fetchPendingActivities();
      await fetchApprovalCounts();
      return response;
    } catch (error) {
      console.error('审批活动失败:', error);
      throw error;
    }
  };

  const rejectActivity = async (id: number, comment?: string) => {
    try {
      const request: ApprovalRequest = { comment };
      const response = await apiClient.post(
        Endpoints.adminApprovals.rejectActivity(id),
        request
      );
      // 刷新列表
      await fetchPendingActivities();
      await fetchApprovalCounts();
      return response;
    } catch (error) {
      console.error('拒绝活动失败:', error);
      throw error;
    }
  };

  // Actions - 待审批资源预约
  const fetchPendingResourceBookings = async (page = 0, size = 10) => {
    loading.value = true;
    try {
      const data = await apiClient.get<ResourceBooking[]>(
        Endpoints.adminApprovals.pendingResourceBookings,
        { params: { page, size } }
      );
      pendingResourceBookings.value = data;
      return data;
    } catch (error) {
      console.error('获取待审批资源预约失败:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const approveResourceBooking = async (id: number, comment?: string) => {
    try {
      const request: ApprovalRequest = { comment };
      const response = await apiClient.post(
        Endpoints.adminApprovals.approveResourceBooking(id),
        request
      );
      await fetchPendingResourceBookings();
      await fetchApprovalCounts();
      return response;
    } catch (error) {
      console.error('审批资源预约失败:', error);
      throw error;
    }
  };

  const rejectResourceBooking = async (id: number, comment?: string) => {
    try {
      const request: ApprovalRequest = { comment };
      const response = await apiClient.post(
        Endpoints.adminApprovals.rejectResourceBooking(id),
        request
      );
      await fetchPendingResourceBookings();
      await fetchApprovalCounts();
      return response;
    } catch (error) {
      console.error('拒绝资源预约失败:', error);
      throw error;
    }
  };

  // Actions - 待审批资金申请
  const fetchPendingFundApplications = async (page = 0, size = 10) => {
    loading.value = true;
    try {
      const data = await apiClient.get<PageResponse<FundApplication>>(
        Endpoints.adminApprovals.pendingFundApplications,
        { params: { page, size } }
      );
      pendingFundApplications.value = data.content;
      return data;
    } catch (error) {
      console.error('获取待审批资金申请失败:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const approveFundApplication = async (id: number, comment?: string) => {
    try {
      const request: ApprovalRequest = { comment };
      const response = await apiClient.post(
        Endpoints.adminApprovals.approveFundApplication(id),
        request
      );
      await fetchPendingFundApplications();
      await fetchApprovalCounts();
      return response;
    } catch (error) {
      console.error('审批资金申请失败:', error);
      throw error;
    }
  };

  const rejectFundApplication = async (id: number, comment?: string) => {
    try {
      const request: ApprovalRequest = { comment };
      const response = await apiClient.post(
        Endpoints.adminApprovals.rejectFundApplication(id),
        request
      );
      await fetchPendingFundApplications();
      await fetchApprovalCounts();
      return response;
    } catch (error) {
      console.error('拒绝资金申请失败:', error);
      throw error;
    }
  };

  // Actions - 审批历史
  const fetchHistoryCounts = async () => {
    try {
      const data = await apiClient.get<HistoryCounts>(
        Endpoints.adminHistory.counts
      );
      historyCounts.value = data;
      return data;
    } catch (error) {
      console.error('获取审批历史统计失败:', error);
      throw error;
    }
  };

  return {
    approvalCounts,
    historyCounts,
    pendingActivities,
    pendingResourceBookings,
    pendingFundApplications,
    loading,
    totalPending,
    fetchApprovalCounts,
    fetchPendingActivities,
    approveActivity,
    rejectActivity,
    fetchPendingResourceBookings,
    approveResourceBooking,
    rejectResourceBooking,
    fetchPendingFundApplications,
    approveFundApplication,
    rejectFundApplication,
    fetchHistoryCounts,
  };
});
