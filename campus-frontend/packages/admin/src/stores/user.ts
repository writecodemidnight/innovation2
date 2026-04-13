import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, UserRole } from '@campus/shared';
import { UserRoleMap } from '@campus/shared';

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
      // TODO: 调用登录API
      // 模拟登录成功
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
      return true;
    } catch (error) {
      console.error('登录失败:', error);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const logout = () => {
    token.value = '';
    userInfo.value = null;
    localStorage.removeItem('admin_token');
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
  };
});