<template>
  <view class="activity-detail-page">
    <!-- 活动封面 -->
    <view class="cover-section">
      <image
        class="cover-image"
        :src="activity.coverImageUrl || '/static/images/default-activity.png'"
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
              {{ activity.currentParticipants }}/{{ activity.maxParticipants || activity.capacity }}人
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

    <!-- 推荐活动 -->
    <view v-if="recommendedActivities.length > 0" class="recommend-section card">
      <view class="section-title">相关推荐</view>
      <view class="recommend-list">
        <ActivityCard
          v-for="item in recommendedActivities"
          :key="item.id"
          :activity="item"
          @click="goToDetail(item.id)"
        />
      </view>
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
import { onShareAppMessage, onShareTimeline } from '@dcloudio/uni-app';
import { ActivityStatus, formatDateTime, Endpoints } from '@campus/shared';
import { apiClient } from '@campus/shared';
import type { Activity, ActivityDetail } from '@campus/shared';
import ActivityCard from '@/components/ActivityCard.vue';
import { useUserStore } from '@/stores/user';

// 活动数据
const activity = ref<Partial<ActivityDetail>>({});
const activityId = ref<number | null>(null);
const recommendedActivities = ref<Activity[]>([]);
const loadingRecommend = ref(false);
const userStore = useUserStore();

const isCollected = ref(false);
const hasJoined = ref(false);

// 计算属性
const remainingQuota = computed(() => {
  const max = activity.value.maxParticipants || activity.value.capacity || 0;
  return max - (activity.value.currentParticipants || 0);
});

const canJoin = computed(() => {
  const max = activity.value.maxParticipants || activity.value.capacity || 0;
  return activity.value.status === ActivityStatus.REGISTERING &&
         !hasJoined.value &&
         remainingQuota.value > 0 &&
         (activity.value.currentParticipants || 0) < max;
});

const joinButtonText = computed(() => {
  const max = activity.value.maxParticipants || activity.value.capacity || 0;
  if (hasJoined.value) return '已报名';
  if (activity.value.status === ActivityStatus.COMPLETED) return '已结束';
  if (activity.value.status === ActivityStatus.CANCELLED) return '已取消';
  if ((activity.value.currentParticipants || 0) >= max) return '名额已满';
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

function goToDetail(id: number) {
  uni.navigateTo({ url: `/pages/activity/detail?id=${id}` });
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

async function onJoin() {
  // 检查登录状态
  if (!userStore.isLoggedIn) {
    uni.showModal({
      title: '请先登录',
      content: '报名活动需要先登录',
      confirmText: '去登录',
      success: (res) => {
        if (res.confirm) {
          uni.navigateTo({ url: '/pages/login/index' });
        }
      },
    });
    return;
  }

  if (!canJoin.value || !activityId.value) return;

  uni.showModal({
    title: '确认报名',
    content: `确定要报名参加"${activity.value.title}"吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await apiClient.post(Endpoints.activities.join(activityId.value!));
          hasJoined.value = true;
          activity.value.currentParticipants = (activity.value.currentParticipants || 0) + 1;
          uni.showToast({ title: '报名成功', icon: 'success' });
        } catch (error: any) {
          uni.showToast({ title: error.message || '报名失败', icon: 'none' });
        }
      }
    },
  });
}

async function loadActivityDetail(id: number) {
  try {
    const data = await apiClient.get<ActivityDetail>(Endpoints.activities.detail(id));
    activity.value = data;
    activityId.value = id;
    // 加载推荐活动
    loadRecommendedActivities(id);
  } catch (error: any) {
    uni.showToast({ title: error.message || '获取活动详情失败', icon: 'none' });
  }
}

// 加载推荐活动
async function loadRecommendedActivities(currentId: number) {
  loadingRecommend.value = true;
  try {
    const data = await apiClient.get<Activity[]>(Endpoints.activities.recommend);
    // 过滤掉当前活动
    recommendedActivities.value = (data || []).filter(a => a.id !== currentId).slice(0, 3);
  } catch (error) {
    console.error('获取推荐活动失败:', error);
    recommendedActivities.value = [];
  } finally {
    loadingRecommend.value = false;
  }
}

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages();
  const currentPage = pages[pages.length - 1];
  const { id } = currentPage.$page?.options || {};
  if (id) {
    loadActivityDetail(Number(id));
  }
});

// 分享给朋友
onShareAppMessage(() => {
  return {
    title: activity.value.title || '精彩活动推荐',
    desc: activity.value.description?.slice(0, 50) || '快来看看这个精彩活动！',
    path: `/pages/activity/detail?id=${activityId.value}`,
    imageUrl: activity.value.coverImageUrl || '/static/logo.png',
  };
});

// 分享到朋友圈
onShareTimeline(() => {
  return {
    title: activity.value.title || '精彩活动推荐',
    query: `id=${activityId.value}`,
    imageUrl: activity.value.coverImageUrl || '/static/logo.png',
  };
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

.recommend-section {
  margin: 20rpx;
  padding: 30rpx;

  .section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 20rpx;
  }
}

.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
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
