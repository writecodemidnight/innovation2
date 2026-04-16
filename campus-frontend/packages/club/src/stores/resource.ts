import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Resource, ResourceReservation, ReservationRequest } from '@campus/shared';
import { resourceApi } from '@/api/resource';

export const useResourceStore = defineStore('resource', () => {
  // State
  const resources = ref<Resource[]>([]);
  const reservations = ref<ResourceReservation[]>([]);
  const currentResource = ref<Resource | null>(null);
  const loading = ref(false);
  const submitting = ref(false);

  // Actions
  const fetchResources = async (type?: string) => {
    loading.value = true;
    try {
      const data = await resourceApi.getList(type);
      resources.value = data || [];
    } catch (error) {
      console.error('获取资源列表失败:', error);
      resources.value = [];
    } finally {
      loading.value = false;
    }
  };

  const fetchResourceDetail = async (id: number) => {
    loading.value = true;
    try {
      const data = await resourceApi.getDetail(id);
      currentResource.value = data;
    } catch (error) {
      console.error('获取资源详情失败:', error);
      currentResource.value = null;
    } finally {
      loading.value = false;
    }
  };

  const fetchMyReservations = async () => {
    loading.value = true;
    try {
      const data = await resourceApi.getMyReservations();
      reservations.value = data || [];
    } catch (error) {
      console.error('获取预约列表失败:', error);
      reservations.value = [];
    } finally {
      loading.value = false;
    }
  };

  const createReservation = async (data: ReservationRequest) => {
    submitting.value = true;
    try {
      const response = await resourceApi.createReservation(data);
      return response;
    } catch (error) {
      console.error('创建预约失败:', error);
      throw error;
    } finally {
      submitting.value = false;
    }
  };

  const cancelReservation = async (id: number) => {
    try {
      await resourceApi.cancelReservation(id);
      // 刷新预约列表
      await fetchMyReservations();
    } catch (error) {
      console.error('取消预约失败:', error);
      throw error;
    }
  };

  return {
    resources,
    reservations,
    currentResource,
    loading,
    submitting,
    fetchResources,
    fetchResourceDetail,
    fetchMyReservations,
    createReservation,
    cancelReservation,
  };
});
