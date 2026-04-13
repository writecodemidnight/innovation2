import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Activity, ActivityListParams, ActivityCreateRequest } from '@campus/shared';

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
      // TODO: 调用API获取活动列表
      // const { data } = await get<ActivityListResponse>(Endpoints.activities.list, { params });
      // activities.value = data.items;
      // total.value = data.total;

      // 模拟数据
      activities.value = [];
      total.value = 0;
    } finally {
      loading.value = false;
    }
  };

  const fetchActivityDetail = async (id: number) => {
    loading.value = true;
    try {
      // TODO: 调用API获取活动详情
      // const data = await get<Activity>(Endpoints.activities.detail(id));
      // currentActivity.value = data;
    } finally {
      loading.value = false;
    }
  };

  const createActivity = async (data: ActivityCreateRequest) => {
    // TODO: 调用API创建活动
    // return await post<Activity>(Endpoints.activities.create, data);
    return null;
  };

  const updateActivity = async (id: number, data: Partial<ActivityCreateRequest>) => {
    // TODO: 调用API更新活动
    // return await put<Activity>(Endpoints.activities.update(id), data);
    return null;
  };

  const deleteActivity = async (id: number) => {
    // TODO: 调用API删除活动
    // return await del(Endpoints.activities.delete(id));
    return null;
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
