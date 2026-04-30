<template>
  <view class="profile-page">
    <!-- 用户信息卡片 -->
    <view class="user-card" :style="{ paddingTop: statusBarHeight + 60 + 'px' }">
      <view class="user-info" @click="handleUserCardClick">
        <image class="avatar" :src="avatarUrl" mode="aspectFill" />
        <view class="user-detail">
          <view class="nickname">{{ user?.realName || user?.username || '点击登录' }}</view>
          <view class="student-id">{{ user?.studentId || user?.role === 'STUDENT' ? '学生用户' : '登录后查看更多信息' }}</view>
        </view>
        <uni-icons type="right" size="20" color="#fff" />
      </view>
      <view class="user-stats">
        <view class="stat-item">
          <text class="stat-num">{{ stats.participated }}</text>
          <text class="stat-label">已参加</text>
        </view>
        <view class="stat-item">
          <text class="stat-num">{{ stats.evaluated }}</text>
          <text class="stat-label">已评价</text>
        </view>
        <view class="stat-item">
          <text class="stat-num">{{ stats.collected }}</text>
          <text class="stat-label">收藏</text>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section card">
      <view class="menu-item" @click="goToHistory">
        <view class="menu-left">
          <uni-icons type="calendar" size="24" color="#1989fa" />
          <text class="menu-text">参与记录</text>
        </view>
        <uni-icons type="right" size="16" color="#999" />
      </view>
      <view class="menu-item" @click="goToEvaluations">
        <view class="menu-left">
          <uni-icons type="star" size="24" color="#ff9800" />
          <text class="menu-text">我的评价</text>
        </view>
        <uni-icons type="right" size="16" color="#999" />
      </view>
      <view class="menu-item" @click="goToCollections">
        <view class="menu-left">
          <uni-icons type="heart" size="24" color="#ff4d4f" />
          <text class="menu-text">我的收藏</text>
        </view>
        <uni-icons type="right" size="16" color="#999" />
      </view>
    </view>

    <!-- 其他功能 -->
    <view class="menu-section card">
      <view class="menu-item" @click="goToFeedback">
        <view class="menu-left">
          <uni-icons type="chatbubble" size="24" color="#07c160" />
          <text class="menu-text">意见反馈</text>
        </view>
        <uni-icons type="right" size="16" color="#999" />
      </view>
      <view class="menu-item" @click="goToAbout">
        <view class="menu-left">
          <uni-icons type="info" size="24" color="#999" />
          <text class="menu-text">关于我们</text>
        </view>
        <uni-icons type="right" size="16" color="#999" />
      </view>
    </view>

    <!-- 退出登录 -->
    <!-- 登录/退出按钮 -->
    <view class="logout-section">
      <button v-if="user" class="logout-btn" @click="logout">退出登录</button>
      <button v-else class="login-btn" @click="goToLogin">立即登录</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useUserStore } from '@/stores/user';
import { Endpoints } from '@campus/shared';
import { apiClient } from '@campus/shared';
import type { User } from '@campus/shared';

interface UserStats {
  participated: number;
  evaluated: number;
  collected: number;
}

const userStore = useUserStore();
const statusBarHeight = ref(20);

const stats = ref<UserStats>({
  participated: 0,
  evaluated: 0,
  collected: 0,
});

// 使用 store 中的用户信息
const user = computed(() => userStore.userInfo);
const isLoggedIn = computed(() => userStore.isLoggedIn);

// 头像URL（使用真实头像或默认SVG）
const avatarUrl = computed(() => {
  if (user.value?.avatarUrl) return user.value.avatarUrl;
  if (user.value?.avatar) return user.value.avatar;
  // 生成带有用户首字母的默认头像
  const name = user.value?.nickname || user.value?.username || '?';
  const initial = name.charAt(0).toUpperCase();
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120"><rect fill="#1989fa" width="120" height="120"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="white" font-size="48">${initial}</text></svg>`;
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
});

onMounted(() => {
  const systemInfo = uni.getSystemInfoSync();
  statusBarHeight.value = systemInfo.statusBarHeight || 20;
  loadUserInfo();
});

async function loadUserInfo() {
  // 先尝试从 store 获取用户信息
  if (!userStore.token) {
    return;
  }

  try {
    await userStore.fetchUserInfo();

    // 获取用户统计数据
    if (user.value?.id) {
      const userStats = await apiClient.get<UserStats>(Endpoints.users.stats(user.value.id));
      stats.value = userStats || { participated: 0, evaluated: 0, collected: 0 };
    }
  } catch (error: any) {
    console.error('获取用户信息失败:', error);
    // Token 过期或无效，会自动退出
  }
}

function goToSettings() {
  uni.navigateTo({ url: '/pages/profile/settings' });
}

function goToHistory() {
  uni.switchTab({ url: '/pages/participate/history' });
}

function goToEvaluations() {
  uni.navigateTo({ url: '/pages/evaluate/list' });
}

function goToCollections() {
  uni.showToast({ title: '功能开发中', icon: 'none' });
}

function goToFeedback() {
  uni.showToast({ title: '功能开发中', icon: 'none' });
}

function goToAbout() {
  uni.showToast({ title: '功能开发中', icon: 'none' });
}

function handleUserCardClick() {
  if (!isLoggedIn.value) {
    goToLogin();
  } else {
    goToSettings();
  }
}

function goToLogin() {
  uni.navigateTo({ url: '/pages/login/index' });
}

async function logout() {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: async (res) => {
      if (res.confirm) {
        await userStore.logout();
        stats.value = { participated: 0, evaluated: 0, collected: 0 };
        uni.showToast({ title: '已退出', icon: 'success' });
      }
    },
  });
}
</script>

<style scoped lang="scss">
.profile-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.user-card {
  background: linear-gradient(135deg, #1989fa 0%, #096dd9 100%);
  padding: 40rpx;
  padding-bottom: 60rpx;
  border-radius: 0 0 40rpx 40rpx;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 40rpx;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.3);
  margin-right: 24rpx;
}

.user-detail {
  flex: 1;
}

.nickname {
  font-size: 40rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
}

.student-id {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}

.user-stats {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 40rpx;
  font-weight: 600;
  color: #fff;
}

.stat-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 8rpx;
}

.menu-section {
  margin: 20rpx;
  padding: 0 20rpx;
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid #f5f5f5;

  &:last-child {
    border-bottom: none;
  }
}

.menu-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.menu-text {
  font-size: 30rpx;
  color: #333;
}

.logout-section {
  margin: 40rpx 20rpx;
}

.logout-btn {
  background: #fff;
  color: #ff4d4f;
  border-radius: 12rpx;
  font-size: 32rpx;
  border: none;

  &::after {
    border: none;
  }
}

.login-btn {
  background: #1989fa;
  color: #fff;
  border-radius: 12rpx;
  font-size: 32rpx;
  border: none;

  &::after {
    border: none;
  }
}
</style>
