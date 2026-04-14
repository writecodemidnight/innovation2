import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { Endpoints, UserRoleMap } from '@campus/shared';
import type { User, LoginResponse } from '@campus/shared';

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(localStorage.getItem('access_token') || '');
  const refreshToken = ref<string>(localStorage.getItem('refresh_token') || '');
  const userInfo = ref<User | null>(null);
  const loading = ref(false);

  // Getters
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value);
  const isClubAdmin = computed(() =>
    userInfo.value?.role === 'CLUB_PRESIDENT' || userInfo.value?.role === 'CLUB_MANAGER'
  );
  const isAdmin = computed(() =>
    userInfo.value?.role === 'ADMIN' || userInfo.value?.role === 'SUPER_ADMIN'
  );
  const roleLabel = computed(() => {
    if (!userInfo.value) return '';
    return UserRoleMap[userInfo.value.role as keyof typeof UserRoleMap]?.label || userInfo.value.role;
  });

  // Actions
  const login = async (credentials: { username: string; password: string }) => {
    loading.value = true;
    try {
      const { data } = await axios.post<LoginResponse>(
        Endpoints.auth.wxLogin,
        credentials
      );
      token.value = data.accessToken;
      refreshToken.value = data.refreshToken;
      userInfo.value = data.user;
      localStorage.setItem('access_token', data.accessToken);
      localStorage.setItem('refresh_token', data.refreshToken);
      return true;
    } catch (error) {
      console.error('登录失败:', error);
      const axiosError = error as { response?: { data?: { message?: string } } };
      ElMessage.error(axiosError.response?.data?.message || '登录失败，请检查用户名和密码');
      return false;
    } finally {
      loading.value = false;
    }
  };

  const logout = () => {
    token.value = '';
    refreshToken.value = '';
    userInfo.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  const refreshAccessToken = async () => {
    if (!refreshToken.value) return false;
    try {
      const { data } = await axios.post<LoginResponse>(Endpoints.auth.refresh, {
        refreshToken: refreshToken.value,
      });
      token.value = data.accessToken;
      localStorage.setItem('access_token', data.accessToken);
      return true;
    } catch {
      logout();
      return false;
    }
  };

  const fetchUserInfo = async () => {
    if (!token.value) return;
    // 后续可调用用户信息API
  };

  // 初始化时尝试恢复用户信息
  const initFromStorage = () => {
    const storedToken = localStorage.getItem('access_token');
    const storedRefreshToken = localStorage.getItem('refresh_token');
    if (storedToken) {
      token.value = storedToken;
      refreshToken.value = storedRefreshToken || '';
      // 标记为需要重新获取用户信息，后续调用API获取完整信息
      userInfo.value = null;
    }
  };

  return {
    token,
    refreshToken,
    userInfo,
    loading,
    isLoggedIn,
    isClubAdmin,
    isAdmin,
    roleLabel,
    login,
    logout,
    refreshAccessToken,
    fetchUserInfo,
    initFromStorage,
  };
});
