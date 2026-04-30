<template>
  <view class="my-evaluations-page">
    <!-- 评价列表 -->
    <scroll-view scroll-y class="evaluation-list" @scrolltolower="onLoadMore">
      <view
        v-for="item in evaluations"
        :key="item.id"
        class="evaluation-card"
        @click="goToDetail(item.activityId)"
      >
        <view class="card-header">
          <image class="activity-image" :src="item.activityCover || 'data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22120%22%20height%3D%22120%22%3E%3Crect%20fill%3D%22%23e0e0e0%22%20width%3D%22120%22%20height%3D%22120%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22%23999%22%20font-size%3D%2220%22%3E%E6%B4%BB%E5%8A%A8%3C%2Ftext%3E%3C%2Fsvg%3E'" mode="aspectFill" />
          <view class="activity-info">
            <text class="activity-title">{{ item.activityTitle }}</text>
            <text class="activity-club">{{ item.clubName }}</text>
          </view>
        </view>

        <view class="card-content">
          <view class="rating-row">
            <uni-rate :value="item.rating" :readonly="true" :size="16" />
            <text class="rating-text">{{ item.rating }}分</text>
          </view>
          <view v-if="item.organizationRating || item.contentRating" class="sub-ratings">
            <text class="sub-rating" v-if="item.organizationRating">组织: {{ item.organizationRating }}分</text>
            <text class="sub-rating" v-if="item.contentRating">内容: {{ item.contentRating }}分</text>
          </view>
          <text class="comment-text">{{ item.content }}</text>

          <!-- 图片预览 -->
          <view v-if="item.images?.length" class="image-preview">
            <image
              v-for="(img, idx) in item.images.slice(0, 3)"
              :key="idx"
              :src="img"
              mode="aspectFill"
              @click.stop="previewImage(item.images, idx)"
            />
          </view>
        </view>

        <view class="card-footer">
          <text class="eval-time">{{ formatTime(item.createdAt) }}</text>
          <view class="sentiment-tag" :class="item.sentimentLevel">
            {{ sentimentLabel(item.sentimentLevel) }}
          </view>
        </view>
      </view>

      <uni-load-more :status="loadMoreStatus" />
    </scroll-view>

    <!-- 空状态 -->
    <view v-if="evaluations.length === 0 && !loading" class="empty-state">
      <uni-icons type="chatbubble" size="48" color="#999" />
      <text class="empty-text">暂无评价记录</text>
      <text class="empty-tip">参加活动后可以评价哦</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { feedbackApi } from '@/api/feedback';

interface Evaluation {
  id: number;
  activityId: number;
  activityTitle: string;
  activityCover: string;
  clubName: string;
  rating: number;
  organizationRating?: number;
  contentRating?: number;
  content: string;
  images?: string[];
  createdAt: string;
  sentimentLevel?: string;
}

const evaluations = ref<Evaluation[]>([]);
const loading = ref(false);
const page = ref(0);
const pageSize = ref(10);
const totalElements = ref(0);

const loadMoreStatus = computed(() => {
  if (loading.value) return 'loading';
  if (evaluations.value.length >= totalElements.value) return 'noMore';
  return 'more';
});

onMounted(() => {
  loadEvaluations();
});

async function loadEvaluations() {
  if (loading.value) return;
  loading.value = true;

  try {
    // 调用反馈API获取我的评价列表
    const response = await feedbackApi.getMyList({
      page: page.value,
      size: pageSize.value,
    });

    if (response?.content) {
      evaluations.value.push(...response.content);
      totalElements.value = response.totalElements || 0;
    }
  } catch (error: any) {
    console.error('获取评价列表失败:', error);
    uni.showToast({ title: error.message || '获取失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
}

function onLoadMore() {
  page.value++;
  loadEvaluations();
}

function goToDetail(activityId: number) {
  uni.navigateTo({ url: `/pages/activity/detail?id=${activityId}` });
}

function previewImage(images: string[], current: number) {
  uni.previewImage({
    urls: images,
    current: images[current],
  });
}

function formatTime(time: string) {
  const date = new Date(time);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

function sentimentLabel(level?: string) {
  const map: Record<string, string> = {
    'POSITIVE': '积极',
    'NEUTRAL': '中性',
    'NEGATIVE': '消极',
  };
  return map[level || ''] || '已评价';
}
</script>

<style scoped lang="scss">
.my-evaluations-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.evaluation-list {
  padding: 20rpx;
}

.evaluation-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f5f5f5;
}

.activity-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 12rpx;
  margin-right: 20rpx;
}

.activity-info {
  flex: 1;
}

.activity-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 8rpx;
  display: block;
}

.activity-club {
  font-size: 26rpx;
  color: #666;
}

.card-content {
  margin-bottom: 20rpx;
}

.rating-row {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.rating-text {
  margin-left: 12rpx;
  font-size: 28rpx;
  color: #ff9800;
  font-weight: 500;
}

.sub-ratings {
  display: flex;
  gap: 20rpx;
  margin-bottom: 12rpx;
}

.sub-rating {
  font-size: 24rpx;
  color: #666;
  background: #f5f5f5;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.comment-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.6;
  display: block;
}

.image-preview {
  display: flex;
  gap: 12rpx;
  margin-top: 16rpx;

  image {
    width: 160rpx;
    height: 160rpx;
    border-radius: 8rpx;
  }
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.eval-time {
  font-size: 24rpx;
  color: #999;
}

.sentiment-tag {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;

  &.POSITIVE {
    color: #07c160;
    background: #e6f7ed;
  }

  &.NEUTRAL {
    color: #1989fa;
    background: #e6f2ff;
  }

  &.NEGATIVE {
    color: #ff4d4f;
    background: #fff1f0;
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
  font-size: 30rpx;
  color: #333;
}

.empty-tip {
  margin-top: 12rpx;
  font-size: 26rpx;
  color: #999;
}
</style>
