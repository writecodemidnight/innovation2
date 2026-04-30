import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@campus/shared';
import { UserRole, UserRoleMap, Endpoints } from '@campus/shared';
import { apiClient } from '@campus/shared/api/client.axios';
import { clearTokenCache } from '@campus/shared/api/client.axios';

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(localStorage.getItem('admin_token') || '');
  const userInfo = ref<User | null>(null);
  const loading = ref(false);

  // Getters
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value);
  const isAdmin = computed(() =>
    userInfo.value?.role === UserRole.ADMIN ||
    userInfo.value?.role === UserRole.SUPER_ADMIN
  );
  const roleLabel = computed(() => {
    if (!userInfo.value) return '';
    return UserRoleMap[userInfo.value.role]?.label || userInfo.value.role;
  });

  // Actions
  const login = async (credentials: { username: string; password: string }) => {
    loading.value = true;
    try {
      // 登录前清除旧token，避免请求时带上旧token导致403
      logout();

      // 调用后端登录API
      const response = await apiClient.post<{ accessToken: string; user: User }>(
        Endpoints.auth.login,
        credentials
      );

      token.value = response.accessToken;
      userInfo.value = response.user;
      localStorage.setItem('admin_token', response.accessToken);
      localStorage.setItem('access_token', response.accessToken); // 兼容 apiClient

      return true;
    } catch (error: any) {
      console.error('登录失败:', error);
      // 如果后端API不可用，降级到模拟登录（开发阶段）
      if (error.message?.includes('Network Error') || error.response?.status === 404) {
        console.warn('后端API不可用，使用模拟登录');
        return mockLogin(credentials);
      }
      return false;
    } finally {
      loading.value = false;
    }
  };

  // 模拟登录（开发阶段备用）
  const mockLogin = (credentials: { username: string; password: string }) => {
    token.value = 'mock_admin_token';
    userInfo.value = {
      id: 1,
      username: credentials.username,
      realName: '管理员',
      role: UserRole.ADMIN,
      status: 'ACTIVE' as any,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    localStorage.setItem('admin_token', token.value);
    localStorage.setItem('access_token', token.value); // 兼容 apiClient
    return true;
  };

  const logout = () => {
    token.value = '';
    userInfo.value = null;
    localStorage.removeItem('admin_token');
    localStorage.removeItem('access_token');
    clearTokenCache();
  };

  const fetchUserInfo = async () => {
    if (!token.value) return;
    try {
      const user = await apiClient.get<User>(Endpoints.auth.profile);
      userInfo.value = user;
    } catch (error) {
      console.error('获取用户信息失败:', error);
      if ((error as any)?.response?.status === 401) {
        logout();
      }
    }
  };

  return {
    token,
    userInfo,
    loading,
    isLoggedIn,
    isAdmin,
    roleLabel,
    login,
    logout,
    fetchUserInfo,
  };
});