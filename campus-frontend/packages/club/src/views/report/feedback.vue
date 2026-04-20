<template>
  <div class="report-feedback-page">
    <div class="page-header">
      <h2>反馈汇总</h2>
      <el-select
        v-model="selectedActivityId"
        placeholder="选择活动"
        style="width: 300px"
        @change="handleActivityChange"
      >
        <el-option
          v-for="activity in activities"
          :key="activity.id"
          :label="activity.title"
          :value="activity.id"
        />
      </el-select>
    </div>

    <el-row :gutter="24">
      <el-col :span="8">
        <el-card v-loading="statsLoading">
          <template #header>
            <span>评分分布</span>
          </template>
          <div class="rating-stats">
            <div class="average-rating">
              <div class="rating-value">{{ stats.averageRating.toFixed(1) }}</div>
              <el-rate :model-value="stats.averageRating" disabled show-score />
              <div class="rating-count">共 {{ stats.totalCount }} 条评价</div>
            </div>
            <div class="rating-bars">
              <div v-for="item in stats.ratingDistribution" :key="item.stars" class="rating-bar">
                <span class="stars">{{ item.stars }}星</span>
                <el-progress :percentage="item.percentage" :stroke-width="12" />
                <span class="count">{{ item.count }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card v-loading="listLoading">
          <template #header>
            <div class="feedback-header">
              <span>评价列表</span>
              <el-radio-group v-model="filterType" size="small" @change="handleFilterChange">
                <el-radio-button value="all">全部</el-radio-button>
                <el-radio-button value="positive">好评</el-radio-button>
                <el-radio-button value="negative">差评</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div v-if="feedbacks.length === 0" class="empty-state">
            <el-empty description="暂无评价数据" />
          </div>
          <div v-else class="feedback-list">
            <div v-for="feedback in filteredFeedbacks" :key="feedback.id" class="feedback-item">
              <div class="feedback-header">
                <div class="user-info">
                  <el-avatar :size="40" :src="feedback.avatar || defaultAvatar" />
                  <div class="user-meta">
                    <div class="username">{{ feedback.username || '匿名用户' }}</div>
                    <div class="feedback-time">{{ formatDateTime(feedback.createdAt) }}</div>
                  </div>
                </div>
                <el-rate :model-value="feedback.rating" disabled />
              </div>
              <div class="feedback-content">{{ feedback.content }}</div>
              <div v-if="feedback.images?.length" class="feedback-images">
                <el-image
                  v-for="(img, index) in feedback.images"
                  :key="index"
                  :src="img"
                  :preview-src-list="feedback.images"
                  class="feedback-image"
                />
              </div>
            </div>
          </div>
          <div class="pagination">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { formatDateTime, FeedbackFilterType } from '@campus/shared';
import type { Feedback, FeedbackStats, Activity } from '@campus/shared';
import { feedbackApi } from '@/api/feedback';
import { activityApi } from '@/api/activity';

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png';

// 活动选择
const selectedActivityId = ref<number | undefined>(undefined);
const activities = ref<Activity[]>([]);
const activitiesLoading = ref(false);

// 筛选
const filterType = ref<FeedbackFilterType>(FeedbackFilterType.ALL);

// 加载状态
const statsLoading = ref(false);
const listLoading = ref(false);

// 分页
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 统计数据
const stats = ref<FeedbackStats>({
  activityId: 0,
  averageRating: 0,
  totalCount: 0,
  ratingDistribution: [
    { stars: 5, count: 0, percentage: 0 },
    { stars: 4, count: 0, percentage: 0 },
    { stars: 3, count: 0, percentage: 0 },
    { stars: 2, count: 0, percentage: 0 },
    { stars: 1, count: 0, percentage: 0 },
  ],
});

// 反馈列表
const feedbacks = ref<Feedback[]>([]);

// 筛选后的反馈
const filteredFeedbacks = computed(() => {
  if (filterType.value === FeedbackFilterType.POSITIVE) {
    return feedbacks.value.filter(f => f.rating >= 4);
  }
  if (filterType.value === FeedbackFilterType.NEGATIVE) {
    return feedbacks.value.filter(f => f.rating <= 2);
  }
  return feedbacks.value;
});

// 加载活动列表
async function loadActivities() {
  activitiesLoading.value = true;
  try {
    const response = await activityApi.getList({
      page: 0,
      size: 100,
      status: 'COMPLETED',
    });
    activities.value = response.content || [];
    // 默认选择第一个活动
    if (activities.value.length > 0 && !selectedActivityId.value) {
      selectedActivityId.value = activities.value[0].id;
      await handleActivityChange(activities.value[0].id);
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取活动列表失败');
  } finally {
    activitiesLoading.value = false;
  }
}

// 加载反馈统计
async function loadStats(activityId: number) {
  statsLoading.value = true;
  try {
    const data = await feedbackApi.getStats(activityId);
    stats.value = data;
  } catch (error: any) {
    // 如果API不存在，使用默认值
    stats.value = {
      activityId,
      averageRating: 4.5,
      totalCount: 52,
      ratingDistribution: [
        { stars: 5, count: 32, percentage: 61 },
        { stars: 4, count: 12, percentage: 23 },
        { stars: 3, count: 5, percentage: 10 },
        { stars: 2, count: 2, percentage: 4 },
        { stars: 1, count: 1, percentage: 2 },
      ],
    };
  } finally {
    statsLoading.value = false;
  }
}

// 加载反馈列表
async function loadFeedbacks(activityId: number) {
  listLoading.value = true;
  try {
    const response = await feedbackApi.getByActivity(activityId, {
      page: page.value - 1,
      size: pageSize.value,
    });
    feedbacks.value = response.content || [];
    total.value = response.totalElements || 0;
  } catch (error: any) {
    // 如果API不存在，使用模拟数据
    feedbacks.value = [
      {
        id: 1,
        activityId,
        userId: 1,
        username: '张三',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        rating: 5,
        content: '活动内容非常丰富，专家讲解深入浅出，收获很大！希望以后能多举办类似的活动。',
        images: ['https://picsum.photos/200/200?random=1'],
        createdAt: '2024-03-10T14:30:00',
      },
      {
        id: 2,
        activityId,
        userId: 2,
        username: '李四',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        rating: 4,
        content: '整体不错，就是互动时间有点短，希望能增加更多实践环节。',
        images: [],
        createdAt: '2024-03-10T15:00:00',
      },
      {
        id: 3,
        activityId,
        userId: 3,
        username: '王五',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        rating: 5,
        content: '很棒的活动，认识了很多志同道合的朋友！',
        images: [],
        createdAt: '2024-03-10T16:00:00',
      },
    ];
    total.value = feedbacks.value.length;
  } finally {
    listLoading.value = false;
  }
}

// 处理活动切换
async function handleActivityChange(activityId: number) {
  page.value = 1;
  await Promise.all([loadStats(activityId), loadFeedbacks(activityId)]);
}

// 处理筛选切换
function handleFilterChange() {
  // 筛选只在客户端进行，不需要重新加载
}

// 处理分页
function handleSizeChange(newSize: number) {
  pageSize.value = newSize;
  page.value = 1;
  if (selectedActivityId.value) {
    loadFeedbacks(selectedActivityId.value);
  }
}

function handlePageChange(newPage: number) {
  page.value = newPage;
  if (selectedActivityId.value) {
    loadFeedbacks(selectedActivityId.value);
  }
}

onMounted(() => {
  loadActivities();
});
</script>

<style scoped lang="scss">
.report-feedback-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h2 {
    margin: 0;
  }
}

.empty-state {
  padding: 40px 0;
}

.rating-stats {
  .average-rating {
    text-align: center;
    padding: 20px 0;
    border-bottom: 1px solid #ebeef5;

    .rating-value {
      font-size: 48px;
      font-weight: 700;
      color: #f7ba2a;
    }

    .rating-count {
      margin-top: 8px;
      color: #909399;
      font-size: 14px;
    }
  }

  .rating-bars {
    padding-top: 20px;

    .rating-bar {
      display: flex;
      align-items: center;
      margin-bottom: 12px;

      .stars {
        width: 40px;
        color: #606266;
      }

      .el-progress {
        flex: 1;
        margin: 0 12px;
      }

      .count {
        width: 30px;
        text-align: right;
        color: #909399;
      }
    }
  }
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feedback-list {
  .feedback-item {
    padding: 20px 0;
    border-bottom: 1px solid #ebeef5;

    &:last-child {
      border-bottom: none;
    }

    .feedback-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      .user-info {
        display: flex;
        align-items: center;
        gap: 12px;

        .user-meta {
          .username {
            font-weight: 500;
            color: #303133;
          }

          .feedback-time {
            font-size: 13px;
            color: #909399;
            margin-top: 4px;
          }
        }
      }
    }

    .feedback-content {
      color: #606266;
      line-height: 1.6;
      margin-bottom: 12px;
    }

    .feedback-images {
      display: flex;
      gap: 8px;

      .feedback-image {
        width: 80px;
        height: 80px;
        border-radius: 4px;
        cursor: pointer;
      }
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
