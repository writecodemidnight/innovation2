<template>
  <view class="activity-detail-page">
    <!-- 活动封面 -->
    <view class="cover-section">
      <image
        class="cover-image"
        :src="activity.coverImageUrl || 'https://picsum.photos/750/400'"
        mode="aspectFill"
      />
      <view class="cover-overlay">
        <view class="status-tag" :class="activity.status">
          {{ getStatusText(activity.status) }}
        </view>
      </view>
    </view>

    <!-- 活动信息 -->
    <view class="info-section card">
      <view class="activity-title">{{ activity.title }}</view>
      <view class="activity-club">
        <uni-icons type="home-filled" size="14" color="#666" />
        <text>{{ activity.clubName }}</text>
      </view>

      <view class="info-list">
        <view class="info-item">
          <uni-icons type="calendar" size="16" color="#1989fa" />
          <view class="info-content">
            <view class="info-label">活动时间</view>
            <view class="info-value">{{ formatDateTime(activity.startTime) }}</view>
          </view>
        </view>
        <view class="info-item">
          <uni-icons type="location" size="16" color="#1989fa" />
          <view class="info-content">
            <view class="info-label">活动地点</view>
            <view class="info-value">{{ activity.location }}</view>
          </view>
        </view>
        <view class="info-item">
          <uni-icons type="personadd" size="16" color="#1989fa" />
          <view class="info-content">
            <view class="info-label">参与人数</view>
            <view class="info-value">
              {{ activity.currentParticipants }}/{{ activity.maxParticipants }}人
              <text class="quota-left">(剩余{{ remainingQuota }}人)</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 活动详情 -->
    <view class="detail-section card">
      <view class="section-title">活动详情</view>
      <view class="detail-content">{{ activity.description }}</view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="bar-left">
        <view class="action-item" @click="onShare">
          <uni-icons type="redo" size="20" />
          <text>分享</text>
        </view>
        <view class="action-item" @click="onCollect">
          <uni-icons :type="isCollected ? 'star-filled' : 'star'" :color="isCollected ? '#ff9800' : '#666'" size="20" />
          <text>收藏</text>
        </view>
      </view>
      <view class="bar-right">
        <button
          class="join-btn"
          :class="{ disabled: !canJoin }"
          :disabled="!canJoin"
          @click="onJoin"
        >
          {{ joinButtonText }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ActivityStatus, formatDateTime } from '@campus/shared';
import type { Activity } from '@campus/shared';

// 活动数据
const activity = ref<Partial<Activity>>({
  id: 1,
  title: '科技创新讲座：AI前沿技术探索',
  description: '本次讲座将邀请业界专家分享人工智能领域的最新进展，包括大语言模型、计算机视觉等前沿技术。欢迎对AI感兴趣的同学积极参加！',
  clubId: 1,
  clubName: '科技创新社',
  activityType: 'LECTURE',
  startTime: new Date(Date.now() + 86400000).toISOString(),
  endTime: new Date(Date.now() + 86400000 + 7200000).toISOString(),
  location: '学生活动中心 301报告厅',
  maxParticipants: 100,
  currentParticipants: 45,
  status: 'REGISTERING' as ActivityStatus,
  coverImageUrl: 'https://picsum.photos/750/400',
});

const isCollected = ref(false);
const hasJoined = ref(false);

// 计算属性
const remainingQuota = computed(() => {
  return (activity.value.maxParticipants || 0) - (activity.value.currentParticipants || 0);
});

const canJoin = computed(() => {
  return activity.value.status === ActivityStatus.REGISTERING &&
         !hasJoined.value &&
         remainingQuota.value > 0;
});

const joinButtonText = computed(() => {
  if (hasJoined.value) return '已报名';
  if (activity.value.status === ActivityStatus.COMPLETED) return '已结束';
  if (activity.value.status === ActivityStatus.CANCELLED) return '已取消';
  if (remainingQuota.value <= 0) return '名额已满';
  return '立即报名';
});

// 方法
function getStatusText(status?: ActivityStatus) {
  const map: Record<string, string> = {
    PLANNING: '筹备中',
    REGISTERING: '报名中',
    ONGOING: '进行中',
    COMPLETED: '已结束',
    CANCELLED: '已取消',
  };
  return status ? (map[status] || status) : '';
}

function onShare() {
  uni.showToast({ title: '分享功能开发中', icon: 'none' });
}

function onCollect() {
  isCollected.value = !isCollected.value;
  uni.showToast({
    title: isCollected.value ? '收藏成功' : '取消收藏',
    icon: 'none',
  });
}

function onJoin() {
  if (!canJoin.value) return;

  uni.showModal({
    title: '确认报名',
    content: `确定要报名参加"${activity.value.title}"吗？`,
    success: (res) => {
      if (res.confirm) {
        // TODO: 调用报名API
        hasJoined.value = true;
        activity.value.currentParticipants = (activity.value.currentParticipants || 0) + 1;
        uni.showToast({ title: '报名成功', icon: 'success' });
      }
    },
  });
}

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages();
  const currentPage = pages[pages.length - 1];
  const { id } = currentPage.$page?.options || {};
  if (id) {
    // TODO: 根据ID获取活动详情
    console.log('活动ID:', id);
  }
});
</script>

<style scoped lang="scss">
.activity-detail-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 120rpx;
}

.cover-section {
  position: relative;
  height: 400rpx;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, transparent 50%, rgba(0,0,0,0.3) 100%);
  padding: 30rpx;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
}

.status-tag {
  padding: 8rpx 20rpx;
  border-radius: 24rpx;
  font-size: 24rpx;
  color: #fff;
  background: #07c160;

  &.COMPLETED, &.CANCELLED {
    background: #999;
  }
}

.info-section {
  margin: 20rpx;
  padding: 30rpx;
}

.activity-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 16rpx;
}

.activity-club {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 26rpx;
  color: #666;
  margin-bottom: 24rpx;
  padding-bottom: 24rpx;
  border-bottom: 1rpx solid #eee;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.info-content {
  flex: 1;
}

.info-label {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 4rpx;
}

.info-value {
  font-size: 28rpx;
  color: #333;
}

.quota-left {
  font-size: 24rpx;
  color: #ff9800;
  margin-left: 8rpx;
}

.detail-section {
  margin: 20rpx;
  padding: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
}

.detail-content {
  font-size: 28rpx;
  color: #666;
  line-height: 1.8;
}

.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 100rpx;
  background: #fff;
  border-top: 1rpx solid #eee;
  display: flex;
  align-items: center;
  padding: 0 30rpx;
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);

  .bar-left {
    display: flex;
    gap: 40rpx;
    margin-right: 30rpx;
  }

  .action-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4rpx;
    font-size: 22rpx;
    color: #666;
  }

  .bar-right {
    flex: 1;
  }
}

.join-btn {
  background: linear-gradient(135deg, #1989fa 0%, #096dd9 100%);
  color: #fff;
  border-radius: 40rpx;
  font-size: 28rpx;
  font-weight: 500;
  border: none;

  &.disabled {
    background: #ccc;
  }
}
</style>
