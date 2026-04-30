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
    <scroll-view
      scroll-y
      class="activity-list"
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="onLoadMore"
    >
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
import { ref, computed, onMounted, watch } from 'vue';
import { ActivityType, ActivityTypeMap, apiClient, Endpoints } from '@campus/shared';
import type { Activity, PageResponse } from '@campus/shared';
import ActivityCard from '@/components/ActivityCard.vue';

const searchKeyword = ref('');
const currentTab = ref('ALL');
const activities = ref<Activity[]>([]);
const loading = ref(false);
const refreshing = ref(false);
const finished = ref(false);
const page = ref(0);
const pageSize = ref(10);
const totalElements = ref(0);

const tabs = [
  { label: '全部', value: 'ALL' },
  ...Object.values(ActivityType).map(type => ({
    label: ActivityTypeMap[type],
    value: type,
  })),
];

const filteredActivities = computed(() => {
  // 前端筛选（基于已加载的数据）
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
  if (finished.value || activities.value.length >= totalElements.value) return 'noMore';
  return 'more';
});

onMounted(() => {
  // 从 URL 参数获取类型
  const pages = getCurrentPages();
  const currentPage = pages[pages.length - 1];
  const { type } = currentPage.$page?.options || {};
  if (type && Object.values(ActivityType).includes(type as ActivityType)) {
    currentTab.value = type;
  }
  loadActivities();
});

// 监听筛选条件变化，重新加载
watch([currentTab], () => {
  activities.value = [];
  page.value = 0;
  finished.value = false;
  loadActivities();
});

async function loadActivities() {
  if (loading.value || finished.value) return;
  loading.value = true;

  try {
    // 构建请求参数
    const params: Record<string, any> = {
      page: page.value,
      size: pageSize.value,
      // 暂时不筛选状态，显示所有活动以便测试
      // status: 'REGISTERING',
    };

    // 如果选择了特定类型，添加类型筛选
    if (currentTab.value !== 'ALL') {
      params.type = currentTab.value;
    }

    // 如果有搜索关键词，添加关键词筛选
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value;
    }

    const response = await apiClient.get<PageResponse<Activity>>(Endpoints.activities.list, { params });

    if (response && response.content) {
      activities.value.push(...response.content);
      totalElements.value = response.totalElements || 0;

      // 判断是否已加载完所有数据
      if (response.content.length < pageSize.value || activities.value.length >= totalElements.value) {
        finished.value = true;
      }
    } else {
      finished.value = true;
    }
  } catch (error: any) {
    console.error('加载活动列表失败:', error);
    uni.showToast({ title: error.message || '加载失败', icon: 'none' });
    finished.value = true;
  } finally {
    loading.value = false;
  }
}

function onLoadMore() {
  page.value++;
  loadActivities();
}

function onSearch() {
  // 搜索时重置列表
  activities.value = [];
  page.value = 0;
  finished.value = false;
  loadActivities();
}

async function onRefresh() {
  refreshing.value = true;
  activities.value = [];
  page.value = 0;
  finished.value = false;
  await loadActivities();
  refreshing.value = false;
  uni.stopPullDownRefresh();
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
