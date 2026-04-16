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
        <text class="section-title">为你推荐</text>
        <text class="section-more" @click="goToMore">查看更多</text>
      </view>

      <scroll-view scroll-y class="activity-list" @scrolltolower="onLoadMore">
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
import { ref, onMounted } from 'vue';
import { ActivityType, ActivityTypeIcon, ActivityTypeMap, Endpoints } from '@campus/shared';
import { apiClient } from '@campus/shared';
import type { Activity } from '@campus/shared';
import ActivityCard from '@/components/ActivityCard.vue';

// 状态栏高度
const statusBarHeight = ref(20);

// 轮播图数据
const banners = ref([
  { image: 'https://picsum.photos/750/300?random=1', link: '' },
  { image: 'https://picsum.photos/750/300?random=2', link: '' },
  { image: 'https://picsum.photos/750/300?random=3', link: '' },
]);

// 分类数据
const categories = Object.values(ActivityType).map(type => ({
  type,
  name: ActivityTypeMap[type],
  icon: ActivityTypeIcon[type],
}));

// 活动列表
const activities = ref<Activity[]>([]);
const loading = ref(false);
const finished = ref(false);
const page = ref(1);
const pageSize = 10;

const loadMoreStatus = ref<'more' | 'loading' | 'noMore'>('more');

// 获取状态栏高度
onMounted(() => {
  const systemInfo = uni.getSystemInfoSync();
  statusBarHeight.value = systemInfo.statusBarHeight || 20;
  loadRecommendations();
});

// 加载推荐活动
async function loadRecommendations() {
  if (loading.value || finished.value) return;

  loading.value = true;
  loadMoreStatus.value = 'loading';

  try {
    const data = await apiClient.get<Activity[]>(Endpoints.activities.recommend);
    if (page.value === 1) {
      activities.value = data || [];
    } else {
      activities.value.push(...(data || []));
    }

    // 如果返回数据少于预期，标记为已结束
    if (!data || data.length < pageSize) {
      finished.value = true;
      loadMoreStatus.value = 'noMore';
    } else {
      loadMoreStatus.value = 'more';
    }
  } catch (error: any) {
    uni.showToast({ title: error.message || '获取推荐活动失败', icon: 'none' });
    // 首次加载失败时显示空状态
    if (page.value === 1) {
      activities.value = [];
    }
    finished.value = true;
    loadMoreStatus.value = 'noMore';
  } finally {
    loading.value = false;
  }
}

// 加载更多
function onLoadMore() {
  if (finished.value || loading.value) return;
  page.value++;
  loadRecommendations();
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
function onBannerClick(banner: any) {
  if (banner.link) {
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
