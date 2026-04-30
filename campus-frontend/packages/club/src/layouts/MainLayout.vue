<template>
  <el-container class="main-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon size="32" color="#409EFF"><School /></el-icon>
        <span class="logo-text">社团管理系统</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#001529"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
          @click="handleMenuClick(item.path)"
        >
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <breadcrumb />
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
import { useUserStore } from '@/stores/user';
import Breadcrumb from '@/components/Breadcrumb.vue';
import {
  School,
  ArrowDown,
  Odometer,
  List,
  Plus,
  Calendar,
  OfficeBuilding,
  DocumentChecked,
  PieChart,
  ChatLineRound,
  Money
} from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const activeMenu = computed(() => route.path);

// 直接定义菜单项，避免路由获取问题
const menuItems = [
  { path: '/club', title: '概览', icon: 'Odometer' },
  { path: '/club/activities', title: '活动列表', icon: 'List' },
  { path: '/club/activities/apply', title: '申报活动', icon: 'Plus' },
  { path: '/club/resources/calendar', title: '资源日历', icon: 'Calendar' },
  { path: '/club/resources/apply', title: '预约资源', icon: 'OfficeBuilding' },
  { path: '/club/resources/status', title: '预约状态', icon: 'DocumentChecked' },
  { path: '/club/reports/radar', title: '效果分析', icon: 'PieChart' },
  { path: '/club/reports/feedback', title: '反馈汇总', icon: 'ChatLineRound' },
  { path: '/club/funds', title: '资金管理', icon: 'Money' },
];

const userAvatar = computed(() => {
  return `https://api.dicebear.com/7.x/avataaars/svg?seed=${userStore.userInfo?.id}`;
});

const handleMenuClick = (path: string) => {
  router.push(path);
};

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/club/profile');
      break;
    case 'logout':
      userStore.logout();
      router.push('/club/login');
      break;
  }
};
</script>

<style scoped lang="scss">
.main-layout {
  min-height: 100vh;
}

.sidebar {
  background: #001529;
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
  justify-content: center;
  background: #002140;
  padding: 0 16px;

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
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 99;
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
    background: #f5f5f5;
  }

  .username {
    margin: 0 8px;
    font-size: 14px;
    color: #606266;
  }
}

.main-content {
  margin-left: 220px;
  background: #f0f2f5;
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
