import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from '@campus/shared/api/client.axios';
import {
  Endpoints,
  type AdminResource,
  type ResourceRequest,
  type ResourceStats,
  type PageResponse,
} from '@campus/shared';

export const useResourceStore = defineStore('resource', () => {
  // State
  const resources = ref<AdminResource[]>([]);
  const currentResource = ref<AdminResource | null>(null);
  const stats = ref<ResourceStats | null>(null);
  const loading = ref(false);

  // Actions - 统计
  const fetchStats = async () => {
    try {
      const data = await apiClient.get<ResourceStats>(
        Endpoints.adminResources.stats
      );
      stats.value = data;
      return data;
    } catch (error) {
      console.error('获取资源统计失败:', error);
      throw error;
    }
  };

  // Actions - 资源列表
  const fetchResources = async (page = 0, size = 10, resourceType?: string, status?: string) => {
    loading.value = true;
    try {
      const params: Record<string, any> = { page, size };
      if (resourceType) params.resourceType = resourceType;
      if (status) params.status = status;

      const data = await apiClient.get<PageResponse<AdminResource>>(
        Endpoints.adminResources.list,
        { params }
      );
      resources.value = data.content;
      return data;
    } catch (error) {
      console.error('获取资源列表失败:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  };

  // Actions - 资源详情
  const fetchResourceDetail = async (id: number) => {
    try {
      const data = await apiClient.get<AdminResource>(
        Endpoints.adminResources.detail(id)
      );
      currentResource.value = data;
      return data;
    } catch (error) {
      console.error('获取资源详情失败:', error);
      throw error;
    }
  };

  // Actions - 创建资源
  const createResource = async (data: ResourceRequest) => {
    try {
      const result = await apiClient.post<AdminResource>(
        Endpoints.adminResources.create,
        data
      );
      // 刷新列表
      await fetchResources();
      await fetchStats();
      return result;
    } catch (error) {
      console.error('创建资源失败:', error);
      throw error;
    }
  };

  // Actions - 更新资源
  const updateResource = async (id: number, data: ResourceRequest) => {
    try {
      const result = await apiClient.post<AdminResource>(
        Endpoints.adminResources.update(id),
        data
      );
      // 刷新列表和当前资源
      await fetchResources();
      if (currentResource.value?.id === id) {
        await fetchResourceDetail(id);
      }
      return result;
    } catch (error) {
      console.error('更新资源失败:', error);
      throw error;
    }
  };

  // Actions - 删除资源
  const deleteResource = async (id: number) => {
    try {
      await apiClient.delete(Endpoints.adminResources.delete(id));
      // 刷新列表
      await fetchResources();
      await fetchStats();
      // 如果删除的是当前查看的资源，清空
      if (currentResource.value?.id === id) {
        currentResource.value = null;
      }
    } catch (error) {
      console.error('删除资源失败:', error);
      throw error;
    }
  };

  return {
    resources,
    currentResource,
    stats,
    loading,
    fetchStats,
    fetchResources,
    fetchResourceDetail,
    createResource,
    updateResource,
    deleteResource,
  };
});
