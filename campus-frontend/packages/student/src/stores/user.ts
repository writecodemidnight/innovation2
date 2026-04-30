import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@campus/shared';
import { apiClient, Endpoints } from '@campus/shared';

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(uni.getStorageSync('access_token') || '');
  const userInfo = ref<User | null>(null);
  const loading = ref(false);

  // 初始化时如果有token，尝试获取用户信息
  async function init() {
    if (token.value && !userInfo.value) {
      await fetchUserInfo();
    }
  }

  // Getters
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value);
  const isStudent = computed(() => userInfo.value?.role === 'STUDENT');

  // Actions

  /**
   * 微信小程序登录
   */
  async function wxLogin(code: string) {
    loading.value = true;
    try {
      const data = await apiClient.post<{ accessToken: string; user: User }>(
        Endpoints.auth.wxLogin,
        { code }
      );

      token.value = data.accessToken;
      userInfo.value = data.user;
      uni.setStorageSync('access_token', data.accessToken);

      return true;
    } catch (error: any) {
      console.error('登录失败:', error);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * 账号密码登录（用于测试）
   */
  async function login(credentials: { username: string; password: string }) {
    loading.value = true;
    try {
      const data = await apiClient.post<{ accessToken: string; user: User }>(
        Endpoints.auth.login,
        credentials
      );

      token.value = data.accessToken;
      userInfo.value = data.user;
      uni.setStorageSync('access_token', data.accessToken);

      return true;
    } catch (error: any) {
      console.error('登录失败:', error);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * 登出
   */
  async function logout() {
    try {
      await apiClient.post(Endpoints.auth.logout);
    } catch (error) {
      // 即使退出API失败也清除本地状态
    }
    token.value = '';
    userInfo.value = null;
    uni.removeStorageSync('access_token');
  }

  /**
   * 获取用户信息
   */
  async function fetchUserInfo() {
    if (!token.value) return;
    try {
      const data = await apiClient.get<User>(Endpoints.auth.profile);
      userInfo.value = data;
    } catch (error: any) {
      console.error('获取用户信息失败:', error);
      if (error.status === 401) {
        logout();
      }
    }
  }

  return {
    token,
    userInfo,
    loading,
    isLoggedIn,
    isStudent,
    init,
    wxLogin,
    login,
    logout,
    fetchUserInfo,
  };
});
