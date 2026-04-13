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
    <scroll-view scroll-y class="history-list" @scrolltolower="onLoadMore">
      <view
        v-for="item in filteredList"
        :key="item.id"
        class="history-card"
        @click="goToDetail(item.activityId)"
      >
        <image class="card-image" :src="item.coverImageUrl" mode="aspectFill" />
        <view class="card-content">
          <view class="card-title">{{ item.title }}</view>
          <view class="card-info">
            <text class="info-text">{{ item.clubName }}</text>
            <text class="info-text">{{ formatDate(item.startTime) }}</text>
          </view>
          <view class="card-status" :class="item.status">
            {{ getStatusText(item.status) }}
          </view>
        </view>
        <view class="card-actions">
          <button
            v-if="item.status === 'COMPLETED' && !item.evaluated"
            class="action-btn"
            @click.stop="goToEvaluate(item.activityId)"
          >
            评价
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

    <!-- 空状态 -->
    <view v-if="filteredList.length === 0" class="empty-state">
      <uni-icons type="info" size="48" color="#999" />
      <text class="empty-text">暂无参与记录</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

interface ParticipationRecord {
  id: number;
  activityId: number;
  title: string;
  clubName: string;
  startTime: string;
  coverImageUrl: string;
  status: 'REGISTERING' | 'ONGOING' | 'COMPLETED' | 'CANCELLED';
  evaluated: boolean;
}

const currentStatus = ref('ALL');
const records = ref<ParticipationRecord[]>([]);
const loading = ref(false);
const finished = ref(false);
const page = ref(1);

const statusTabs = [
  { label: '全部', value: 'ALL' },
  { label: '待参加', value: 'REGISTERING' },
  { label: '进行中', value: 'ONGOING' },
  { label: '已完成', value: 'COMPLETED' },
];

const filteredList = computed(() => {
  if (currentStatus.value === 'ALL') return records.value;
  return records.value.filter(r => r.status === currentStatus.value);
});

const loadMoreStatus = computed(() => {
  if (loading.value) return 'loading';
  if (finished.value) return 'noMore';
  return 'more';
});

onMounted(() => {
  loadRecords();
});

function loadRecords() {
  if (loading.value || finished.value) return;
  loading.value = true;

  // 模拟数据
  const mockData: ParticipationRecord[] = Array.from({ length: 5 }, (_, i) => ({
    id: i + 1,
    activityId: i + 1,
    title: `精彩活动 ${i + 1}`,
    clubName: '科技创新社',
    startTime: new Date(Date.now() + 86400000 * (i - 2)).toISOString(),
    coverImageUrl: `https://picsum.photos/200/200?random=${i}`,
    status: ['REGISTERING', 'ONGOING', 'COMPLETED', 'COMPLETED', 'CANCELLED'][i] as any,
    evaluated: i === 2,
  }));

  records.value.push(...mockData);
  loading.value = false;
  if (page.value >= 3) finished.value = true;
}

function onLoadMore() {
  page.value++;
  loadRecords();
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

function cancelParticipation(id: number) {
  uni.showModal({
    title: '确认取消',
    content: '确定要取消参加这个活动吗？',
    success: (res) => {
      if (res.confirm) {
        // TODO: 调用取消API
        uni.showToast({ title: '已取消', icon: 'success' });
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

  &.cancel {
    background: #f5f5f5;
    color: #666;
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
</style>
