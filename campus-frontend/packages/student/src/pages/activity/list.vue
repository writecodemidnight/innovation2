<template>
  <view class="activity-list-page">
    <!-- 搜索栏 -->
    <view class="search-bar">
      <uni-search-bar v-model="searchKeyword" placeholder="搜索活动" @confirm="onSearch" />
    </view>

    <!-- 筛选标签 -->
    <scroll-view scroll-x class="filter-tabs">
      <view
        v-for="tab in tabs"
        :key="tab.value"
        class="tab-item"
        :class="{ active: currentTab === tab.value }"
        @click="currentTab = tab.value"
      >
        {{ tab.label }}
      </view>
    </scroll-view>

    <!-- 活动列表 -->
    <scroll-view scroll-y class="activity-list" @scrolltolower="onLoadMore">
      <ActivityCard
        v-for="activity in filteredActivities"
        :key="activity.id"
        :activity="activity"
        @click="goToDetail(activity.id)"
      />
      <uni-load-more :status="loadMoreStatus" />
    </scroll-view>

    <!-- 空状态 -->
    <view v-if="filteredActivities.length === 0" class="empty-state">
      <uni-icons type="info" size="48" color="#999" />
      <text class="empty-text">暂无活动</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ActivityType, ActivityTypeMap } from '@campus/shared';
import type { Activity } from '@campus/shared';
import ActivityCard from '@/components/ActivityCard.vue';

const searchKeyword = ref('');
const currentTab = ref('ALL');
const activities = ref<Activity[]>([]);
const loading = ref(false);
const finished = ref(false);
const page = ref(1);

const tabs = [
  { label: '全部', value: 'ALL' },
  ...Object.values(ActivityType).map(type => ({
    label: ActivityTypeMap[type],
    value: type,
  })),
];

const filteredActivities = computed(() => {
  let result = activities.value;
  if (currentTab.value !== 'ALL') {
    result = result.filter(a => a.activityType === currentTab.value);
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase();
    result = result.filter(a =>
      a.title.toLowerCase().includes(kw) ||
      a.description?.toLowerCase().includes(kw)
    );
  }
  return result;
});

const loadMoreStatus = computed(() => {
  if (loading.value) return 'loading';
  if (finished.value) return 'noMore';
  return 'more';
});

onMounted(() => {
  loadActivities();
});

function loadActivities() {
  if (loading.value || finished.value) return;
  loading.value = true;

  // 模拟数据
  const mockData: Activity[] = Array.from({ length: 10 }, (_, i) => ({
    id: i + 1,
    title: `精彩活动 ${i + 1}`,
    description: '这是一个精彩的社团活动，欢迎大家踊跃参加！',
    clubId: 1,
    clubName: '科技创新社',
    organizerId: 1,
    activityType: Object.values(ActivityType)[i % 5],
    startTime: new Date(Date.now() + 86400000 * (i + 1)).toISOString(),
    endTime: new Date(Date.now() + 86400000 * (i + 1) + 7200000).toISOString(),
    location: '学生活动中心 301',
    maxParticipants: 50,
    currentParticipants: 20 + i * 3,
    status: 'REGISTERING' as any,
    coverImageUrl: `https://picsum.photos/400/200?random=${i}`,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }));

  activities.value.push(...mockData);
  loading.value = false;
  if (page.value >= 3) finished.value = true;
}

function onLoadMore() {
  page.value++;
  loadActivities();
}

function onSearch() {
  // 搜索逻辑
}

function goToDetail(id: number) {
  uni.navigateTo({ url: `/pages/activity/detail?id=${id}` });
}
</script>

<style scoped lang="scss">
.activity-list-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.search-bar {
  padding: 20rpx;
  background: #fff;
}

.filter-tabs {
  background: #fff;
  padding: 0 20rpx 20rpx;
  white-space: nowrap;
}

.tab-item {
  display: inline-block;
  padding: 12rpx 24rpx;
  margin-right: 16rpx;
  font-size: 26rpx;
  color: #666;
  background: #f5f5f5;
  border-radius: 32rpx;

  &.active {
    color: #fff;
    background: #1989fa;
  }
}

.activity-list {
  height: calc(100vh - 200rpx);
  padding: 20rpx;
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
</style>
