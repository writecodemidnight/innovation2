<template>
  <view class="home-page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <text class="nav-title">校园社团活动</text>
        <view class="nav-search" @click="goToSearch">
          <uni-icons type="search" size="16" color="#999" />
          <text class="search-placeholder">搜索活动</text>
        </view>
      </view>
    </view>

    <!-- 轮播图 -->
    <view class="banner-section">
      <swiper class="swiper" :indicator-dots="true" :autoplay="true" :interval="3000" indicator-color="rgba(255,255,255,0.5)" indicator-active-color="#fff">
        <swiper-item v-for="(item, index) in banners" :key="index" @click="onBannerClick(item)">
          <image class="banner-image" :src="item.image" mode="aspectFill" />
        </swiper-item>
      </swiper>
    </view>

    <!-- 活动分类 -->
    <view class="category-section card">
      <view
        v-for="cat in categories"
        :key="cat.type"
        class="category-item"
        @click="goToCategory(cat.type)"
      >
        <view class="category-icon">{{ cat.icon }}</view>
        <text class="category-name">{{ cat.name }}</text>
      </view>
    </view>

    <!-- 推荐活动 -->
    <view class="recommend-section">
      <view class="section-header">
        <text class="section-title">{{ userStore.isLoggedIn ? '为你推荐' : '热门活动' }}</text>
        <text class="section-more" @click="goToMore">查看更多</text>
      </view>

      <scroll-view
        scroll-y
        class="activity-list"
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
        @scrolltolower="onLoadMore"
      >
        <ActivityCard
          v-for="activity in activities"
          :key="activity.id"
          :activity="activity"
          @click="goToDetail(activity.id)"
        />
        <uni-load-more :status="loadMoreStatus" />
      </scroll-view>
    </view>

    <!-- 空状态 -->
    <view v-if="!loading && activities.length === 0" class="empty-state">
      <uni-icons type="info" size="48" color="#999" />
      <text class="empty-text">暂无推荐活动</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { ActivityType, ActivityTypeIcon, ActivityTypeMap, Endpoints } from '@campus/shared';
import { apiClient } from '@campus/shared';
import { useActivityStore } from '@/stores/activity';
import { useUserStore } from '@/stores/user';
import ActivityCard from '@/components/ActivityCard.vue';
import type { Activity } from '@campus/shared';

const activityStore = useActivityStore();
const userStore = useUserStore();

// 状态栏高度
const statusBarHeight = ref(20);

// 轮播图数据（从热门活动中获取带封面的活动）
const banners = ref<{ image: string; link: string; activityId?: number }[]>([]);

// 加载轮播图（使用热门活动的前3个带封面的活动）
async function loadBanners() {
  try {
    const data = await apiClient.get<Activity[]>(Endpoints.activities.hot);
    const activitiesWithCover = (data || [])
      .filter(a => a.coverImageUrl)
      .slice(0, 3)
      .map(a => ({
        image: a.coverImageUrl!,
        link: `/pages/activity/detail?id=${a.id}`,
        activityId: a.id,
      }));

    // 如果没有带封面的活动，使用默认占位图
    if (activitiesWithCover.length === 0) {
      banners.value = [
        { image: 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22750%22%20height%3D%22300%22%3E%3Crect%20fill%3D%22linear-gradient(135deg%2C%23667eea%200%25%2C%23764ba2%20100%25)%22%20width%3D%22750%22%20height%3D%22300%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22white%22%20font-size%3D%2236%22%3E%E6%A0%A1%E5%9B%AD%E7%A4%BE%E5%9B%A2%E6%B4%BB%E5%8A%A8%3C%2Ftext%3E%3C%2Fsvg%3E', link: '', activityId: undefined },
      ];
    } else {
      banners.value = activitiesWithCover;
    }
  } catch (error) {
    console.error('加载轮播图失败:', error);
    banners.value = [{ image: 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22750%22%20height%3D%22300%22%3E%3Crect%20fill%3D%22%23e0e0e0%22%20width%3D%22750%22%20height%3D%22300%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22%23999%22%20font-size%3D%2236%22%3E%E6%A0%A1%E5%9B%AD%E7%A4%BE%E5%9B%A2%E6%B4%BB%E5%8A%A8%3C%2Ftext%3E%3C%2Fsvg%3E', link: '' }];
  }
}

// 分类数据
const categories = Object.values(ActivityType).map(type => ({
  type,
  name: ActivityTypeMap[type],
  icon: ActivityTypeIcon[type],
}));

// 本地状态存储活动列表
const localActivities = ref<Activity[]>([]);
const localLoading = ref(false);
const refreshing = ref(false);

// 从store获取活动列表（登录时使用推荐，未登录时使用热门）
const activities = computed(() => {
  if (userStore.isLoggedIn) {
    return activityStore.recommendedActivities;
  }
  return localActivities.value;
});
const loading = computed(() => {
  if (userStore.isLoggedIn) {
    return activityStore.loading;
  }
  return localLoading.value;
});
const loadMoreStatus = computed(() => {
  if (loading.value) return 'loading' as const;
  return 'more' as const;
});

// 获取状态栏高度
onMounted(() => {
  const systemInfo = uni.getSystemInfoSync();
  statusBarHeight.value = systemInfo.statusBarHeight || 20;
  // 延迟加载，避免页面初始化阻塞
  setTimeout(() => {
    loadBanners();
    loadRecommendations();
  }, 100);
});

// 加载推荐活动（未登录时使用热门活动）
async function loadRecommendations() {
  if (userStore.isLoggedIn) {
    await activityStore.fetchRecommendedActivities();
  } else {
    // 未登录时加载热门活动
    localLoading.value = true;
    try {
      const data = await apiClient.get<Activity[]>(Endpoints.activities.hot);
      localActivities.value = data || [];
    } catch (error) {
      console.error('获取热门活动失败:', error);
      localActivities.value = [];
    } finally {
      localLoading.value = false;
    }
  }
}

// 下拉刷新
async function onRefresh() {
  refreshing.value = true;
  await loadRecommendations();
  refreshing.value = false;
  uni.stopPullDownRefresh();
}

// 加载更多
function onLoadMore() {
  // 推荐活动一次性加载，不需要分页
}

// 跳转到搜索
function goToSearch() {
  uni.navigateTo({ url: '/pages/activity/list' });
}

// 跳转到分类
function goToCategory(type: ActivityType) {
  uni.navigateTo({
    url: `/pages/activity/list?type=${type}`,
  });
}

// 跳转到活动详情
function goToDetail(id: number) {
  uni.navigateTo({
    url: `/pages/activity/detail?id=${id}`,
  });
}

// 跳转到更多
function goToMore() {
  uni.navigateTo({ url: '/pages/activity/list' });
}

// 轮播图点击
function onBannerClick(banner: { image: string; link: string; activityId?: number }) {
  if (banner.activityId) {
    uni.navigateTo({ url: `/pages/activity/detail?id=${banner.activityId}` });
  } else if (banner.link) {
    uni.navigateTo({ url: banner.link });
  }
}
</script>

<style scoped lang="scss">
.home-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.nav-bar {
  background: linear-gradient(135deg, #1989fa 0%, #096dd9 100%);
  padding-bottom: 20rpx;
}

.nav-content {
  display: flex;
  align-items: center;
  padding: 0 30rpx;
  height: 88rpx;
}

.nav-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  margin-right: 24rpx;
}

.nav-search {
  flex: 1;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 32rpx;
  padding: 12rpx 24rpx;
}

.search-placeholder {
  font-size: 26rpx;
  color: #999;
  margin-left: 12rpx;
}

.banner-section {
  margin: 20rpx;
  border-radius: 16rpx;
  overflow: hidden;
}

.swiper {
  height: 300rpx;
}

.banner-image {
  width: 100%;
  height: 300rpx;
}

.category-section {
  display: flex;
  flex-wrap: wrap;
  padding: 24rpx 12rpx;
}

.category-item {
  width: 25%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx 0;
}

.category-icon {
  width: 88rpx;
  height: 88rpx;
  background: linear-gradient(135deg, #e6f2ff 0%, #f0f7ff 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  margin-bottom: 12rpx;
}

.category-name {
  font-size: 24rpx;
  color: #666;
}

.recommend-section {
  padding: 0 20rpx 40rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.section-more {
  font-size: 26rpx;
  color: #1989fa;
}

.activity-list {
  height: calc(100vh - 600rpx);
}
</style>
