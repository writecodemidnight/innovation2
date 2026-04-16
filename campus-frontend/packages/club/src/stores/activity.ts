import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Activity, ActivityListParams, ActivityCreateRequest } from '@campus/shared';
import { activityApi } from '@/api/activity';

export const useActivityStore = defineStore('activity', () => {
  // State
  const activities = ref<Activity[]>([]);
  const currentActivity = ref<Activity | null>(null);
  const loading = ref(false);
  const total = ref(0);

  // Actions
  const fetchActivities = async (params: ActivityListParams = {}) => {
    loading.value = true;
    try {
      const response = await activityApi.getList(params);
      activities.value = response.content || [];
      total.value = response.totalElements || 0;
    } catch (error) {
      activities.value = [];
      total.value = 0;
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const fetchActivityDetail = async (id: number) => {
    loading.value = true;
    try {
      const data = await activityApi.getDetail(id);
      currentActivity.value = data;
      return data;
    } catch (error) {
      currentActivity.value = null;
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const createActivity = async (data: ActivityCreateRequest) => {
    return await activityApi.create(data);
  };

  const updateActivity = async (id: number, data: Partial<ActivityCreateRequest>) => {
    return await activityApi.update(id, data);
  };

  const deleteActivity = async (id: number) => {
    return await activityApi.delete(id);
  };

  return {
    activities,
    currentActivity,
    loading,
    total,
    fetchActivities,
    fetchActivityDetail,
    createActivity,
    updateActivity,
    deleteActivity,
  };
});
