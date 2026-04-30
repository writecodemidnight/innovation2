<template>
  <el-container class="main-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon size="32" color="#00d4aa"><Monitor /></el-icon>
        <span class="logo-text">管理控制台</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
        background-color="#0f1419"
        text-color="#8b949e"
        active-text-color="#00d4aa"
      >
        <el-menu-item
          v-for="route in menuRoutes"
          :key="route.path"
          :index="route.path"
          :route="route"
        >
          <el-icon>
            <component :is="route.meta?.icon" />
          </el-icon>
          <template #title>{{ route.meta?.title }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2 class="page-title">{{ $route.meta?.title }}</h2>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="userAvatar" />
              <span class="username">{{ userStore.userInfo?.realName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const activeMenu = computed(() => route.path);

const menuRoutes = computed(() => {
  const routes = router.getRoutes();
  console.log('[Menu] All routes:', routes.map(r => ({ path: r.path, name: r.name, children: r.children?.map(c => c.path) })));

  // 查找根路由（可能是 '/' 或 '/admin' 或 ''）
  let mainRoute = routes.find(r => r.path === '/' && r.children?.length > 0);
  if (!mainRoute) {
    mainRoute = routes.find(r => r.path === '' && r.children?.length > 0);
  }
  if (!mainRoute && routes.length > 0) {
    // 如果找不到，取第一个有 children 的路由
    mainRoute = routes.find(r => r.children && r.children.length > 0);
  }

  console.log('[Menu] Main route found:', mainRoute);
  const children = mainRoute?.children?.filter(r => !r.meta?.hidden) || [];
  console.log('[Menu] Menu items:', children.map(c => ({ path: c.path, title: c.meta?.title })));
  return children;
});

const userAvatar = computed(() => {
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${userStore.userInfo?.id}`;
});

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      break;
    case 'logout':
      userStore.logout();
      router.push('/login');
      break;
  }
};
</script>

<style scoped lang="scss">
.main-layout {
  min-height: 100vh;
  background: #0a0e14;
}

.sidebar {
  background: #0f1419;
  border-right: 1px solid #21262d;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #21262d;

  .logo-text {
    color: #fff;
    font-size: 18px;
    font-weight: 600;
    margin-left: 12px;
  }
}

.sidebar-menu {
  border-right: none;
  height: calc(100% - 64px);
}

.header {
  background: #0f1419;
  border-bottom: 1px solid #21262d;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 99;
}

.page-title {
  color: #fff;
  font-size: 18px;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background 0.3s;

  &:hover {
    background: #21262d;
  }

  .username {
    margin: 0 8px;
    font-size: 14px;
    color: #c9d1d9;
  }
}

.main-content {
  margin-left: 220px;
  background: #0a0e14;
  min-height: calc(100vh - 60px);
  padding: 24px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>