<template>
  <view class="activity-card" @click="$emit('click')">
    <image class="card-cover" :src="activity.coverImageUrl || 'https://picsum.photos/400/200'" mode="aspectFill" />
    <view class="card-content">
      <view class="card-header">
        <text class="status-tag" :class="statusClass">{{ statusLabel }}</text>
        <text class="type-tag">{{ typeLabel }}</text>
      </view>
      <text class="card-title">{{ activity.title }}</text>
      <text class="card-desc ellipsis-2">{{ activity.description }}</text>
      <view class="card-info">
        <view class="info-item">
          <uni-icons type="location" size="14" color="#999" />
          <text class="info-text">{{ activity.location }}</text>
        </view>
        <view class="info-item">
          <uni-icons type="calendar" size="14" color="#999" />
          <text class="info-text">{{ formatTime(activity.startTime) }}</text>
        </view>
      </view>
      <view class="card-footer">
        <view class="organizer">
          <image class="org-avatar" :src="clubLogo" mode="aspectFill" />
          <text class="org-name">{{ activity.clubName || '未知社团' }}</text>
        </view>
        <view class="participants">
          <text class="participant-count">{{ activity.currentParticipants }}/{{ activity.maxParticipants }}</text>
          <text class="participant-text">人已报名</text>
        </view>
      </view>
      <view class="progress-bar">
        <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Activity } from '@campus/shared';
import { ActivityStatusMap, ActivityTypeMap, formatDateTime } from '@campus/shared';

const props = defineProps<{
  activity: Activity;
}>();

defineEmits<{
  click: [];
}>();

// 状态标签样式
const statusClass = computed(() => {
  const map: Record<string, string> = {
    'REGISTERING': 'success',
    'ONGOING': 'primary',
    'COMPLETED': 'default',
    'CANCELLED': 'danger',
    'PENDING_APPROVAL': 'warning',
  };
  return map[props.activity.status] || 'default';
});

const statusLabel = computed(() => {
  return ActivityStatusMap[props.activity.status]?.label || props.activity.status;
});

// 类型标签
const typeLabel = computed(() => {
  return ActivityTypeMap[props.activity.activityType] || props.activity.activityType;
});

// 社团Logo
const clubLogo = computed(() => {
  return `https://picsum.photos/40/40?random=${props.activity.clubId}`;
});

// 进度百分比
const progressPercent = computed(() => {
  return Math.min(
    100,
    Math.round((props.activity.currentParticipants / props.activity.maxParticipants) * 100)
  );
});

// 格式化时间
function formatTime(time: string) {
  return formatDateTime(time, 'MM-DD HH:mm');
}
</script>

<style scoped lang="scss">
.activity-card {
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-cover {
  width: 100%;
  height: 280rpx;
}

.card-content {
  padding: 20rpx;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
  gap: 12rpx;
}

.status-tag {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;

  &.success {
    color: #07c160;
    background: #e6f7ed;
  }

  &.primary {
    color: #1989fa;
    background: #e6f2ff;
  }

  &.danger {
    color: #ff4d4f;
    background: #fff1f0;
  }

  &.warning {
    color: #ff9800;
    background: #fff5e6;
  }

  &.default {
    color: #999;
    background: #f5f5f5;
  }
}

.type-tag {
  font-size: 22rpx;
  color: #666;
  background: #f5f5f5;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 8rpx;
  display: block;
}

.card-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.5;
  margin-bottom: 16rpx;
}

.card-info {
  margin-bottom: 16rpx;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8rpx;
  gap: 8rpx;
}

.info-text {
  font-size: 24rpx;
  color: #999;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.organizer {
  display: flex;
  align-items: center;
}

.org-avatar {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  margin-right: 8rpx;
}

.org-name {
  font-size: 24rpx;
  color: #666;
}

.participants {
  display: flex;
  align-items: center;
}

.participant-count {
  font-size: 28rpx;
  font-weight: 600;
  color: #1989fa;
}

.participant-text {
  font-size: 22rpx;
  color: #999;
  margin-left: 4rpx;
}

.progress-bar {
  height: 6rpx;
  background: #ebeef5;
  border-radius: 3rpx;
  margin-top: 16rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1989fa, #096dd9);
  border-radius: 3rpx;
  transition: width 0.3s ease;
}
</style>
