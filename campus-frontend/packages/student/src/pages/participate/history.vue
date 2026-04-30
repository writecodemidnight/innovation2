<template>
  <view class="history-page">
    <!-- 状态筛选 -->
    <view class="status-tabs">
      <view
        v-for="tab in statusTabs"
        :key="tab.value"
        class="tab-item"
        :class="{ active: currentStatus === tab.value }"
        @click="currentStatus = tab.value"
      >
        {{ tab.label }}
      </view>
    </view>

    <!-- 参与记录列表 -->
    <scroll-view
      v-if="userStore.isLoggedIn"
      scroll-y
      class="history-list"
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
    >
      <view
        v-for="item in filteredList"
        :key="item.id"
        class="history-card"
        @click="goToDetail(item.id)"
      >
        <image class="card-image" :src="item.coverImageUrl || 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22160%22%20height%3D%22160%22%3E%3Crect%20fill%3D%22%23e0e0e0%22%20width%3D%22160%22%20height%3D%22160%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22%23999%22%20font-size%3D%2224%22%3E%E6%B4%BB%E5%8A%A8%3C%2Ftext%3E%3C%2Fsvg%3E'" mode="aspectFill" />
        <view class="card-content">
          <view class="card-title">{{ item.title }}</view>
          <view class="card-info">
            <text class="info-text">{{ item.clubName || '未知社团' }}</text>
            <text class="info-text">{{ formatDate(item.startTime) }}</text>
          </view>
          <view class="card-status" :class="item.status">
            {{ getStatusText(item.status) }}
          </view>
        </view>
        <view class="card-actions">
          <button
            v-if="item.status === 'COMPLETED' && !item.hasFeedback"
            class="action-btn"
            @click.stop="goToEvaluate(item.id)"
          >
            评价
          </button>
          <button
            v-if="item.status === 'COMPLETED' && item.hasFeedback"
            class="action-btn disabled"
            disabled
          >
            已评价
          </button>
          <button
            v-if="item.status === 'ONGOING' && !item.checkedIn"
            class="action-btn primary"
            @click.stop="handleCheckIn(item.id)"
          >
            签到
          </button>
          <button
            v-if="item.checkedIn"
            class="action-btn disabled"
            disabled
          >
            已签到
          </button>
          <button
            v-if="item.status === 'REGISTERING'"
            class="action-btn cancel"
            @click.stop="cancelParticipation(item.id)"
          >
            取消
          </button>
        </view>
      </view>
      <uni-load-more :status="loadMoreStatus" />
    </scroll-view>

    <!-- 未登录状态 -->
    <view v-if="!userStore.isLoggedIn" class="empty-state">
      <uni-icons type="person" size="48" color="#999" />
      <text class="empty-text">请先登录查看参与记录</text>
      <button class="login-btn" @click="goToLogin">去登录</button>
    </view>

    <!-- 空状态 -->
    <view v-else-if="filteredList.length === 0" class="empty-state">
      <uni-icons type="info" size="48" color="#999" />
      <text class="empty-text">暂无参与记录</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useActivityStore } from '@/stores/activity';
import { useUserStore } from '@/stores/user';
import { feedbackApi } from '@/api/feedback';

interface ParticipationRecord {
  id: number;
  activityId: number;
  title: string;
  clubName: string;
  startTime: string;
  coverImageUrl: string;
  status: string;
  evaluated: boolean;
  checkedIn: boolean;
  hasFeedback?: boolean;
}

const activityStore = useActivityStore();
const userStore = useUserStore();

const currentStatus = ref('ALL');
const loading = ref(false);
const refreshing = ref(false);

const statusTabs = [
  { label: '全部', value: 'ALL' },
  { label: '待参加', value: 'REGISTERING' },
  { label: '进行中', value: 'ONGOING' },
  { label: '已完成', value: 'COMPLETED' },
];

const filteredList = computed(() => {
  const activities = activityStore.myActivities;
  if (currentStatus.value === 'ALL') return activities;
  return activities.filter(a => a.status === currentStatus.value);
});

const loadMoreStatus = computed(() => {
  if (activityStore.loading) return 'loading';
  return 'noMore';
});

onMounted(() => {
  loadRecords();
});

async function loadRecords() {
  loading.value = true;
  await activityStore.fetchMyActivities();
  // 检查每个活动的评价状态
  await checkFeedbackStatus();
  loading.value = false;
}

async function checkFeedbackStatus() {
  const activities = activityStore.myActivities;
  for (const activity of activities) {
    if (activity.status === 'COMPLETED' && activity.id && !isNaN(activity.id)) {
      try {
        const hasFeedback = await feedbackApi.hasFeedback(activity.id);
        activity.hasFeedback = hasFeedback;
      } catch (e) {
        activity.hasFeedback = false;
      }
    }
  }
}

async function onRefresh() {
  refreshing.value = true;
  await loadRecords();
  refreshing.value = false;
  uni.stopPullDownRefresh();
}

function onLoadMore() {
  // 我的活动不需要分页
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr);
  return `${date.getMonth() + 1}月${date.getDate()}日`;
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    REGISTERING: '待参加',
    ONGOING: '进行中',
    COMPLETED: '已完成',
    CANCELLED: '已取消',
  };
  return map[status] || status;
}

function goToDetail(id: number) {
  uni.navigateTo({ url: `/pages/activity/detail?id=${id}` });
}

function goToEvaluate(id: number) {
  uni.navigateTo({ url: `/pages/evaluate/form?id=${id}` });
}

function goToLogin() {
  uni.navigateTo({ url: '/pages/login/index' });
}

async function handleCheckIn(activityId: number) {
  uni.showModal({
    title: '确认签到',
    content: '确定要签到吗？签到后将无法取消报名。',
    confirmText: '签到',
    success: async (res) => {
      if (res.confirm) {
        const success = await activityStore.checkInActivity(activityId);
        if (success) {
          uni.showToast({ title: '签到成功', icon: 'success' });
          await loadRecords();
        } else {
          uni.showToast({ title: activityStore.error || '签到失败', icon: 'none' });
        }
      }
    },
  });
}

async function cancelParticipation(activityId: number) {
  uni.showModal({
    title: '确认取消',
    content: '确定要取消参加这个活动吗？',
    success: async (res) => {
      if (res.confirm) {
        const success = await activityStore.leaveActivity(activityId);
        if (success) {
          uni.showToast({ title: '已取消报名', icon: 'success' });
          await loadRecords();
        } else {
          uni.showToast({ title: activityStore.error || '取消失败', icon: 'none' });
        }
      }
    },
  });
}
</script>

<style scoped lang="scss">
.history-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.status-tabs {
  display: flex;
  background: #fff;
  padding: 20rpx;
  gap: 16rpx;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 28rpx;
  color: #666;
  background: #f5f5f5;
  border-radius: 8rpx;

  &.active {
    color: #fff;
    background: #1989fa;
  }
}

.history-list {
  height: calc(100vh - 120rpx);
  padding: 20rpx;
}

.history-card {
  display: flex;
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.card-image {
  width: 160rpx;
  height: 160rpx;
  border-radius: 12rpx;
  margin-right: 20rpx;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.card-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.info-text {
  font-size: 24rpx;
  color: #999;
}

.card-status {
  font-size: 24rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  display: inline-block;
  width: fit-content;

  &.REGISTERING {
    color: #1989fa;
    background: #e6f2ff;
  }

  &.ONGOING {
    color: #07c160;
    background: #e6f7ed;
  }

  &.COMPLETED {
    color: #999;
    background: #f5f5f5;
  }

  &.CANCELLED {
    color: #ff4d4f;
    background: #fff1f0;
  }
}

.card-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 16rpx;
}

.action-btn {
  font-size: 24rpx;
  padding: 12rpx 24rpx;
  border-radius: 8rpx;
  background: #1989fa;
  color: #fff;
  border: none;

  &.primary {
    background: #07c160;
  }

  &.cancel {
    background: #f5f5f5;
    color: #666;
  }

  &.disabled {
    background: #e5e5e5;
    color: #999;
  }

  &::after {
    border: none;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 200rpx;
}

.empty-text {
  margin-top: 20rpx;
  font-size: 28rpx;
  color: #999;
}

.login-btn {
  margin-top: 40rpx;
  background: #1989fa;
  color: #fff;
  border-radius: 12rpx;
  padding: 16rpx 48rpx;
  font-size: 30rpx;
  border: none;

  &::after {
    border: none;
  }
}
</style>
