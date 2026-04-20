import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@campus/shared';
import { UserRole, UserRoleMap, Endpoints } from '@campus/shared';
import { apiClient, clearTokenCache } from '@campus/shared/api/client.axios';

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(localStorage.getItem('access_token') || '');
  const userInfo = ref<User | null>(null);
  const loading = ref(false);

  // Getters
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value);
  const isClubAdmin = computed(() => userInfo.value?.role === UserRole.CLUB_PRESIDENT);
  const isAdmin = computed(() => userInfo.value?.role === UserRole.ADMIN || userInfo.value?.role === UserRole.SUPER_ADMIN);
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

      const response = await apiClient.post<{ accessToken: string; user: User }>(
        Endpoints.auth.login,
        credentials
      );
      token.value = response.accessToken;
      userInfo.value = response.user;
      localStorage.setItem('access_token', response.accessToken);
      return true;
    } catch (error: any) {
      console.error('登录失败:', error);
      // 抛出错误让调用者处理
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const logout = () => {
    token.value = '';
    userInfo.value = null;
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
      // 如果获取失败，清除登录状态
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
    isClubAdmin,
    isAdmin,
    roleLabel,
    login,
    logout,
    fetchUserInfo,
  };
});
