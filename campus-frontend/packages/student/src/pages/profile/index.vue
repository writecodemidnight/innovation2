<template>
  <view class="profile-page">
    <!-- 用户信息卡片 -->
    <view class="user-card" :style="{ paddingTop: statusBarHeight + 60 + 'px' }">
      <view class="user-info">
        <image class="avatar" :src="user?.avatar || '/static/images/default-avatar.png'" mode="aspectFill" />
        <view class="user-detail">
          <view class="nickname">{{ user?.realName || user?.username || '未登录' }}</view>
          <view class="student-id">{{ user?.studentId || '点击登录' }}</view>
        </view>
        <uni-icons type="right" size="20" color="#fff" @click="goToSettings" />
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
    <view v-if="user" class="logout-section">
      <button class="logout-btn" @click="logout">退出登录</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Endpoints } from '@campus/shared';
import { apiClient } from '@campus/shared';
import type { User } from '@campus/shared';

interface UserStats {
  participated: number;
  evaluated: number;
  collected: number;
}

const statusBarHeight = ref(20);
const user = ref<User | null>(null);

const stats = ref<UserStats>({
  participated: 0,
  evaluated: 0,
  collected: 0,
});

onMounted(() => {
  const systemInfo = uni.getSystemInfoSync();
  statusBarHeight.value = systemInfo.statusBarHeight || 20;
  loadUserInfo();
});

async function loadUserInfo() {
  try {
    const data = await apiClient.get<User>(Endpoints.auth.profile);
    user.value = data;
    // 获取用户统计数据
    if (data?.id) {
      const userStats = await apiClient.get<UserStats>(Endpoints.users.stats(data.id));
      stats.value = userStats || { participated: 0, evaluated: 0, collected: 0 };
    }
  } catch (error: any) {
    // 未登录或获取失败
    user.value = null;
  }
}

function goToSettings() {
  uni.navigateTo({ url: '/pages/profile/settings' });
}

function goToHistory() {
  uni.switchTab({ url: '/pages/participate/history' });
}

function goToEvaluations() {
  uni.showToast({ title: '功能开发中', icon: 'none' });
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

async function logout() {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await apiClient.post(Endpoints.auth.logout);
        } catch (error) {
          // 即使退出API失败也清除本地状态
        }
        user.value = null;
        uni.removeStorageSync('access_token');
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
}
</style>
