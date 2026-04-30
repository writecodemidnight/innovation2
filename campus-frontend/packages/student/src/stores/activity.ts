import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Activity, ActivityDetail } from '@campus/shared';
import { activityApi } from '../api/activity';

export const useActivityStore = defineStore('activity', () => {
  // State
  const activities = ref<Activity[]>([]);
  const recommendedActivities = ref<Activity[]>([]);
  const hotActivities = ref<Activity[]>([]);
  const upcomingActivities = ref<Activity[]>([]);
  const currentActivity = ref<ActivityDetail | null>(null);
  const myActivities = ref<Activity[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const totalElements = ref(0);
  const currentPage = ref(0);
  const pageSize = ref(10);
  const hasMore = ref(true);

  // Getters
  const isLoading = computed(() => loading.value);
  const hasError = computed(() => !!error.value);

  // Actions

  /**
   * 获取推荐活动
   */
  async function fetchRecommendedActivities() {
    loading.value = true;
    error.value = null;
    try {
      const data = await activityApi.getRecommended();
      recommendedActivities.value = data || [];
    } catch (e: any) {
      console.error('获取推荐活动失败:', e);
      error.value = e.message || '获取推荐活动失败';
      recommendedActivities.value = [];
    } finally {
      loading.value = false;
    }
  }

  /**
   * 获取热门活动
   */
  async function fetchHotActivities() {
    loading.value = true;
    error.value = null;
    try {
      const data = await activityApi.getHot();
      hotActivities.value = data || [];
    } catch (e: any) {
      console.error('获取热门活动失败:', e);
      error.value = e.message || '获取热门活动失败';
      hotActivities.value = [];
    } finally {
      loading.value = false;
    }
  }

  /**
   * 获取即将开始的活动
   */
  async function fetchUpcomingActivities() {
    loading.value = true;
    error.value = null;
    try {
      const data = await activityApi.getUpcoming();
      upcomingActivities.value = data || [];
    } catch (e: any) {
      console.error('获取即将开始活动失败:', e);
      error.value = e.message || '获取即将开始活动失败';
      upcomingActivities.value = [];
    } finally {
      loading.value = false;
    }
  }

  /**
   * 获取活动列表
   */
  async function fetchActivities(params?: {
    page?: number;
    size?: number;
    type?: string;
    status?: string;
    keyword?: string;
    reset?: boolean;
  }) {
    if (params?.reset) {
      activities.value = [];
      currentPage.value = 0;
      hasMore.value = true;
    }

    if (loading.value || !hasMore.value) return;

    loading.value = true;
    error.value = null;
    try {
      const response = await activityApi.getList({
        page: currentPage.value,
        size: pageSize.value,
        ...params
      });

      if (response && response.content) {
        if (params?.reset) {
          activities.value = response.content;
        } else {
          activities.value.push(...response.content);
        }
        totalElements.value = response.totalElements || 0;
        currentPage.value++;
        hasMore.value = activities.value.length < totalElements.value;
      } else {
        hasMore.value = false;
      }
    } catch (e: any) {
      console.error('获取活动列表失败:', e);
      error.value = e.message || '获取活动列表失败';
      hasMore.value = false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * 获取活动详情
   */
  async function fetchActivityDetail(id: number) {
    loading.value = true;
    error.value = null;
    try {
      const data = await activityApi.getDetail(id);
      currentActivity.value = data;
    } catch (e: any) {
      console.error('获取活动详情失败:', e);
      error.value = e.message || '获取活动详情失败';
      currentActivity.value = null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * 获取我的活动
   */
  async function fetchMyActivities() {
    loading.value = true;
    error.value = null;
    try {
      const data = await activityApi.getMyActivities();
      myActivities.value = data || [];
    } catch (e: any) {
      console.error('获取我的活动失败:', e);
      error.value = e.message || '获取我的活动失败';
      myActivities.value = [];
    } finally {
      loading.value = false;
    }
  }

  /**
   * 报名活动
   */
  async function joinActivity(id: number) {
    loading.value = true;
    try {
      await activityApi.join(id);
      // 更新当前活动状态
      if (currentActivity.value?.id === id) {
        currentActivity.value.isRegistered = true;
        currentActivity.value.currentParticipants++;
      }
      return true;
    } catch (e: any) {
      console.error('报名活动失败:', e);
      error.value = e.message || '报名活动失败';
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * 取消报名
   */
  async function leaveActivity(id: number) {
    loading.value = true;
    try {
      await activityApi.leave(id);
      // 更新当前活动状态
      if (currentActivity.value?.id === id) {
        currentActivity.value.isRegistered = false;
        currentActivity.value.currentParticipants--;
      }
      return true;
    } catch (e: any) {
      console.error('取消报名失败:', e);
      error.value = e.message || '取消报名失败';
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * 活动签到
   */
  async function checkInActivity(id: number) {
    loading.value = true;
    try {
      await activityApi.checkIn(id);
      return true;
    } catch (e: any) {
      console.error('签到失败:', e);
      error.value = e.message || '签到失败';
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * 提交评价（星级打分+文字评价，后端自动进行NLP情感分析）
   */
  async function submitEvaluation(id: number, data: {
    rating: number;
    organizationRating?: number;
    contentRating?: number;
    content: string;
    photos?: string[];
  }) {
    loading.value = true;
    try {
      // 导入feedbackApi提交评价
      const { feedbackApi } = await import('@/api/feedback');
      await feedbackApi.submit({
        activityId: id,
        rating: data.rating,
        organizationRating: data.organizationRating,
        contentRating: data.contentRating,
        content: data.content,
        images: data.photos,
      });
      return true;
    } catch (e: any) {
      console.error('提交评价失败:', e);
      error.value = e.message || '提交评价失败';
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * 清除当前活动
   */
  function clearCurrentActivity() {
    currentActivity.value = null;
  }

  /**
   * 清除错误
   */
  function clearError() {
    error.value = null;
  }

  /**
   * 重置分页状态
   */
  function resetPagination() {
    activities.value = [];
    currentPage.value = 0;
    hasMore.value = true;
    totalElements.value = 0;
  }

  return {
    activities,
    recommendedActivities,
    hotActivities,
    upcomingActivities,
    currentActivity,
    myActivities,
    loading,
    error,
    totalElements,
    hasMore,
    isLoading,
    hasError,
    fetchRecommendedActivities,
    fetchHotActivities,
    fetchUpcomingActivities,
    fetchActivities,
    fetchActivityDetail,
    fetchMyActivities,
    joinActivity,
    leaveActivity,
    checkInActivity,
    submitEvaluation,
    clearCurrentActivity,
    clearError,
    resetPagination,
  };
});

