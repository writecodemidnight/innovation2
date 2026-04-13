<template>
  <div class="report-feedback-page">
    <div class="page-header">
      <h2>反馈汇总</h2>
      <el-select v-model="selectedActivity" placeholder="选择活动" style="width: 300px">
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
        <el-card>
          <template #header>
            <span>评分分布</span>
          </template>
          <div class="rating-stats">
            <div class="average-rating">
              <div class="rating-value">{{ averageRating }}</div>
              <el-rate :model-value="averageRating" disabled show-score />
              <div class="rating-count">共 {{ totalCount }} 条评价</div>
            </div>
            <div class="rating-bars">
              <div v-for="item in ratingDistribution" :key="item.stars" class="rating-bar">
                <span class="stars">{{ item.stars }}星</span>
                <el-progress :percentage="item.percentage" :stroke-width="12" />
                <span class="count">{{ item.count }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="feedback-header">
              <span>评价列表</span>
              <el-radio-group v-model="filterType" size="small">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="positive">好评</el-radio-button>
                <el-radio-button label="negative">差评</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="feedback-list">
            <div v-for="feedback in filteredFeedbacks" :key="feedback.id" class="feedback-item">
              <div class="feedback-header">
                <div class="user-info">
                  <el-avatar :size="40" :src="feedback.avatar" />
                  <div class="user-meta">
                    <div class="username">{{ feedback.username }}</div>
                    <div class="feedback-time">{{ feedback.time }}</div>
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
              layout="prev, pager, next"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const selectedActivity = ref('');
const filterType = ref('all');
const page = ref(1);
const pageSize = ref(10);
const total = ref(52);

const activities = ref([
  { id: 1, title: '科技创新讲座' },
  { id: 2, title: '编程工作坊' },
]);

const averageRating = ref(4.5);
const totalCount = ref(52);

const ratingDistribution = ref([
  { stars: 5, count: 32, percentage: 61 },
  { stars: 4, count: 12, percentage: 23 },
  { stars: 3, count: 5, percentage: 10 },
  { stars: 2, count: 2, percentage: 4 },
  { stars: 1, count: 1, percentage: 2 },
]);

const feedbacks = ref([
  {
    id: 1,
    username: '张三',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    time: '2024-03-10 14:30',
    rating: 5,
    content: '活动内容非常丰富，专家讲解深入浅出，收获很大！希望以后能多举办类似的活动。',
    images: ['https://picsum.photos/200/200?random=1'],
  },
  {
    id: 2,
    username: '李四',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    time: '2024-03-10 15:00',
    rating: 4,
    content: '整体不错，就是互动时间有点短，希望能增加更多实践环节。',
    images: [],
  },
  {
    id: 3,
    username: '王五',
    avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    time: '2024-03-10 16:00',
    rating: 5,
    content: '很棒的活动，认识了很多志同道合的朋友！',
    images: [],
  },
]);

const filteredFeedbacks = computed(() => {
  if (filterType.value === 'positive') {
    return feedbacks.value.filter(f => f.rating >= 4);
  }
  if (filterType.value === 'negative') {
    return feedbacks.value.filter(f => f.rating <= 2);
  }
  return feedbacks.value;
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
