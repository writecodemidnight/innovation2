import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Activity, ActivityDetail } from '@campus/shared';
import { activityApi } from '../api/activity';

export const useActivityStore = defineStore('activity', () => {
  // State
  const activities = ref<Activity[]>([]);
  const recommendedActivities = ref<Activity[]>([]);
  const hotActivities = ref<Activity[]>([]);
  const currentActivity = ref<ActivityDetail | null>(null);
  const myActivities = ref<Activity[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

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
      const response = await activityApi.getRecommended();
      recommendedActivities.value = response.data || [];
    } catch (e: any) {
      console.error('获取推荐活动失败:', e);
      error.value = e.message || '获取推荐活动失败';
      // 使用模拟数据作为降级
      recommendedActivities.value = getMockActivities();
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
      const response = await activityApi.getHot();
      hotActivities.value = response.data || [];
    } catch (e: any) {
      console.error('获取热门活动失败:', e);
      error.value = e.message || '获取热门活动失败';
      hotActivities.value = getMockActivities();
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
  }) {
    loading.value = true;
    error.value = null;
    try {
      const response = await activityApi.getList(params);
      activities.value = response.data?.content || [];
    } catch (e: any) {
      console.error('获取活动列表失败:', e);
      error.value = e.message || '获取活动列表失败';
      activities.value = getMockActivities();
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
      const response = await activityApi.getDetail(id);
      currentActivity.value = response.data;
    } catch (e: any) {
      console.error('获取活动详情失败:', e);
      error.value = e.message || '获取活动详情失败';
      currentActivity.value = null;
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
   * 提交评价
   */
  async function submitEvaluation(id: number, data: {
    rating: number;
    content: string;
    photos?: string[];
  }) {
    loading.value = true;
    try {
      await activityApi.submitEvaluation(id, data);
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

  return {
    activities,
    recommendedActivities,
    hotActivities,
    currentActivity,
    myActivities,
    loading,
    error,
    isLoading,
    hasError,
    fetchRecommendedActivities,
    fetchHotActivities,
    fetchActivities,
    fetchActivityDetail,
    joinActivity,
    leaveActivity,
    submitEvaluation,
    clearCurrentActivity,
    clearError,
  };
});

// 模拟数据（用于API不可用时降级）
function getMockActivities(): Activity[] {
  return [
    {
      id: 1,
      title: '人工智能前沿技术讲座',
      description: '邀请业内专家分享AI最新技术趋势',
      type: '学术讲座',
      location: '大礼堂',
      startTime: '2024-04-20T14:00:00',
      endTime: '2024-04-20T16:00:00',
      maxParticipants: 200,
      currentParticipants: 150,
      status: 'APPROVED',
      clubId: 1,
      clubName: '科技创新社',
      posterUrl: '/static/images/activity1.jpg',
      isRegistered: false,
    },
    {
      id: 2,
      title: '春季摄影大赛',
      description: '记录校园春天的美好瞬间',
      type: '文艺比赛',
      location: '校园各角落',
      startTime: '2024-04-15T08:00:00',
      endTime: '2024-04-30T18:00:00',
      maxParticipants: 500,
      currentParticipants: 320,
      status: 'ONGOING',
      clubId: 2,
      clubName: '摄影协会',
      posterUrl: '/static/images/activity2.jpg',
      isRegistered: true,
    },
    {
      id: 3,
      title: '篮球友谊赛',
      description: '各院系篮球友谊交流赛',
      type: '体育竞技',
      location: '体育馆',
      startTime: '2024-04-25T16:00:00',
      endTime: '2024-04-25T18:00:00',
      maxParticipants: 100,
      currentParticipants: 80,
      status: 'APPROVED',
      clubId: 3,
      clubName: '篮球协会',
      posterUrl: '/static/images/activity3.jpg',
      isRegistered: false,
    },
  ];
}
