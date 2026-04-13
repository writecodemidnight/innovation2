import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, UserRole } from '@campus/shared';
import { UserRoleMap } from '@campus/shared';

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(localStorage.getItem('access_token') || '');
  const userInfo = ref<User | null>(null);
  const loading = ref(false);

  // Getters
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value);
  const isClubAdmin = computed(() => userInfo.value?.role === UserRole.CLUB_PRESIDENT);
  const isAdmin = computed(() => userInfo.value?.role === UserRole.ADMIN);
  const roleLabel = computed(() => {
    if (!userInfo.value) return '';
    return UserRoleMap[userInfo.value.role]?.label || userInfo.value.role;
  });

  // Actions
  const login = async (credentials: { username: string; password: string }) => {
    loading.value = true;
    try {
      // TODO: 连接后端登录API
      // 示例：
      // const { data } = await apiClient.post(Endpoints.auth.login, credentials);
      // token.value = data.accessToken;
      // userInfo.value = data.user;
      // localStorage.setItem('access_token', data.accessToken);

      // 开发阶段：模拟登录成功
      // 模拟不同角色：admin 开头为管理员，其他为社团
      const isAdmin = credentials.username.startsWith('admin');
      token.value = 'mock_token_' + Date.now();
      userInfo.value = {
        id: 1,
        username: credentials.username,
        realName: isAdmin ? '系统管理员' : '社团负责人',
        role: isAdmin ? UserRole.ADMIN : UserRole.CLUB_PRESIDENT,
        status: 'ACTIVE' as any,
        clubId: isAdmin ? undefined : 1,
        clubName: isAdmin ? undefined : '科技创新社',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      localStorage.setItem('access_token', token.value);
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
    localStorage.removeItem('access_token');
  };

  const fetchUserInfo = async () => {
    if (!token.value) return;
    // TODO: 调用获取用户信息API
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
