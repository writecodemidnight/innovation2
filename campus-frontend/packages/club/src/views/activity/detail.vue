<template>
  <div class="activity-detail-page">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.back()">返回</el-button>
        <h2>活动详情</h2>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleEdit">编辑</el-button>
        <el-button type="danger" @click="handleDelete">删除</el-button>
      </div>
    </div>

    <el-row :gutter="24">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-tag :type="getStatusType(activity.status)">{{ getStatusLabel(activity.status) }}</el-tag>
            </div>
          </template>

          <div class="activity-info">
            <h3 class="activity-title">{{ activity.title }}</h3>
            <p class="activity-desc">{{ activity.description }}</p>

            <el-descriptions :column="2" border>
              <el-descriptions-item label="活动类型">{{ getActivityTypeLabel(activity.activityType) }}</el-descriptions-item>
              <el-descriptions-item label="社团">{{ activity.clubName }}</el-descriptions-item>
              <el-descriptions-item label="开始时间">{{ formatDateTime(activity.startTime) }}</el-descriptions-item>
              <el-descriptions-item label="结束时间">{{ formatDateTime(activity.endTime) }}</el-descriptions-item>
              <el-descriptions-item label="活动地点">{{ activity.location }}</el-descriptions-item>
              <el-descriptions-item label="人数限制">{{ activity.maxParticipants }}人</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>

        <el-card class="stats-card">
          <template #header>
            <span>参与统计</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-value">{{ activity.currentParticipants }}</div>
                <div class="stat-label">已报名</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-value">{{ activity.maxParticipants - activity.currentParticipants }}</div>
                <div class="stat-label">剩余名额</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-value">{{ Math.round((activity.currentParticipants / activity.maxParticipants) * 100) }}%</div>
                <div class="stat-label">报名率</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>效果评估</span>
          </template>
          <div v-if="activity.evaluation" class="evaluation-section">
            <div class="score-display">
              <div class="score-value">{{ activity.evaluation.score }}</div>
              <el-rate :model-value="activity.evaluation.score / 20" disabled show-score />
            </div>
            <el-divider />
            <div class="evaluation-metrics">
              <div v-for="(value, key) in activity.evaluation.metrics" :key="key" class="metric-item">
                <span class="metric-label">{{ key }}</span>
                <el-progress :percentage="value" />
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无评估数据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { formatDateTime, ActivityStatusMap, ActivityTypeMap } from '@campus/shared';
import type { Activity } from '@campus/shared';

const route = useRoute();
const router = useRouter();

const activity = ref<Partial<Activity>>({
  id: 1,
  title: '科技创新讲座',
  description: '本次讲座将邀请业界专家分享人工智能领域的最新进展。',
  clubId: 1,
  clubName: '科技创新社',
  activityType: 'LECTURE',
  startTime: new Date(Date.now() + 86400000).toISOString(),
  endTime: new Date(Date.now() + 86400000 + 7200000).toISOString(),
  location: '学生活动中心 301报告厅',
  maxParticipants: 100,
  currentParticipants: 45,
  status: 'REGISTERING',
  evaluation: {
    score: 85,
    metrics: {
      '参与度': 90,
      '满意度': 85,
      '互动性': 80,
    }
  }
});

function getStatusType(status: string) {
  const map: Record<string, string> = {
    REGISTERING: 'success',
    ONGOING: 'warning',
    COMPLETED: 'info',
    CANCELLED: 'danger',
  };
  return map[status] || 'info';
}

function getStatusLabel(status: string) {
  return ActivityStatusMap[status as any]?.label || status;
}

function getActivityTypeLabel(type: string) {
  return ActivityTypeMap[type as any] || type;
}

function handleEdit() {
  router.push(`/activities/edit/${activity.value.id}`);
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除该活动吗？', '提示', { type: 'warning' });
    // TODO: 调用删除API
    ElMessage.success('删除成功');
    router.push('/activities');
  } catch {
    // 取消删除
  }
}

onMounted(() => {
  const { id } = route.params;
  if (id) {
    // TODO: 根据ID加载活动详情
    console.log('活动ID:', id);
  }
});
</script>

<style scoped lang="scss">
.activity-detail-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    h2 {
      margin: 0;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-info {
  .activity-title {
    margin: 0 0 16px 0;
    font-size: 20px;
  }

  .activity-desc {
    color: #666;
    margin-bottom: 24px;
    line-height: 1.6;
  }
}

.stats-card {
  margin-top: 24px;
}

.stat-item {
  text-align: center;

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #409eff;
  }

  .stat-label {
    font-size: 14px;
    color: #666;
    margin-top: 8px;
  }
}

.evaluation-section {
  .score-display {
    text-align: center;
    padding: 20px 0;

    .score-value {
      font-size: 48px;
      font-weight: 700;
      color: #409eff;
    }
  }

  .evaluation-metrics {
    .metric-item {
      margin-bottom: 16px;

      .metric-label {
        display: block;
        margin-bottom: 8px;
        color: #666;
      }
    }
  }
}
</style>
