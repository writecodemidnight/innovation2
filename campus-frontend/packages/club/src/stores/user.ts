import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, UserRole } from '@campus/shared';
import { UserRoleMap, Endpoints } from '@campus/shared';
import { apiClient, clearTokenCache } from '@campus/shared';

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(localStorage.getItem('access_token') || '');
  const userInfo = ref<User | null>(null);
  const loading = ref(false);

  // Getters
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value);
  const isClubAdmin = computed(() => userInfo.value?.role === UserRole.CLUB_PRESIDENT || userInfo.value?.role === UserRole.CLUB_MANAGER);
  const isAdmin = computed(() => userInfo.value?.role === UserRole.ADMIN || userInfo.value?.role === UserRole.SUPER_ADMIN);
  const roleLabel = computed(() => {
    if (!userInfo.value) return '';
    return UserRoleMap[userInfo.value.role]?.label || userInfo.value.role;
  });

  // Actions
  const login = async (credentials: { username: string; password: string }) => {
    loading.value = true;
    try {
      // 开发阶段：直接使用模拟登录
      console.warn('开发阶段：使用模拟登录');
      return mockLogin(credentials);

      // 生产环境使用以下代码：
      // const response = await apiClient.post<{ accessToken: string; user: User }>(
      //   Endpoints.auth.login,
      //   credentials
      // );
      // token.value = response.accessToken;
      // userInfo.value = response.user;
      // localStorage.setItem('access_token', response.accessToken);
      // return true;
    } catch (error: any) {
      console.error('登录失败:', error);
      return false;
    } finally {
      loading.value = false;
    }
  };

  // 模拟登录（开发阶段备用）
  const mockLogin = (credentials: { username: string; password: string }) => {
    const isAdminUser = credentials.username.startsWith('admin');
    token.value = 'mock_token_' + Date.now();
    userInfo.value = {
      id: 1,
      username: credentials.username,
      realName: isAdminUser ? '系统管理员' : '社团负责人',
      role: (isAdminUser ? 'ADMIN' : 'CLUB_PRESIDENT') as UserRole,
      status: 'ACTIVE' as any,
      clubId: isAdminUser ? undefined : 1,
      clubName: isAdminUser ? undefined : '科技创新社',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    localStorage.setItem('access_token', token.value);
    return true;
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
