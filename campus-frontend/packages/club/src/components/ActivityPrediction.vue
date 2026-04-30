<template>
  <el-card class="activity-prediction">
    <template #header>
      <div class="card-header">
        <span>智能预测</span>
        <el-tag size="small" type="success">AI</el-tag>
      </div>
    </template>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="prediction" class="prediction-content">
      <!-- 预测参与人数 -->
      <div class="prediction-item main">
        <div class="label">预计参与人数</div>
        <div class="value">
          <span class="number">{{ prediction.predicted_participants }}</span>
          <span class="unit">人</span>
        </div>
        <div class="confidence">
          置信区间: {{ prediction.confidence_lower }} - {{ prediction.confidence_upper }}
        </div>
      </div>

      <!-- 置信度和趋势 -->
      <div class="prediction-row">
        <div class="prediction-item">
          <div class="label">置信度</div>
          <el-progress
            :percentage="Math.round(prediction.confidence_score * 100)"
            :status="getConfidenceStatus(prediction.confidence_score)"
          />
        </div>
        <div class="prediction-item">
          <div class="label">趋势</div>
          <el-tag :type="getTrendType(prediction.trend)">
            {{ prediction.trend }}
          </el-tag>
        </div>
      </div>

      <!-- 建议 -->
      <div v-if="prediction.recommendations?.length" class="recommendations">
        <div class="label">优化建议</div>
        <ul>
          <li v-for="(rec, index) in prediction.recommendations" :key="index">
            {{ rec }}
          </li>
        </ul>
      </div>
    </div>

    <div v-else class="empty-state">
      <el-empty description="暂无预测数据" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { predictParticipation } from '@/api/algorithm';
import { ElMessage } from 'element-plus';

interface Prediction {
  predicted_participants: number;
  confidence_lower: number;
  confidence_upper: number;
  confidence_score: number;
  trend: string;
  recommendations: string[];
}

const props = defineProps<{
  activityType: string;
  venueType?: string;
  plannedDate: string;
}>();

const loading = ref(false);
const prediction = ref<Prediction | null>(null);

const getConfidenceStatus = (score: number) => {
  if (score >= 0.8) return 'success';
  if (score >= 0.6) return '';
  return 'exception';
};

const getTrendType = (trend: string) => {
  if (trend === '上升') return 'success';
  if (trend === '下降') return 'danger';
  return 'info';
};

const loadPrediction = async () => {
  loading.value = true;
  try {
    const response = await predictParticipation({
      activityType: props.activityType,
      venueType: props.venueType || 'default',
      plannedDate: props.plannedDate,
    });
    prediction.value = response as Prediction;
  } catch (error: any) {
    ElMessage.error('预测加载失败');
    console.error('Prediction error:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadPrediction();
});
</script>

<style scoped lang="scss">
.activity-prediction {
  margin-top: 16px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .loading-state {
    padding: 20px 0;
  }

  .prediction-content {
    .prediction-item {
      &.main {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #ebeef5;
        margin-bottom: 16px;

        .label {
          color: #606266;
          font-size: 14px;
          margin-bottom: 8px;
        }

        .value {
          .number {
            font-size: 36px;
            font-weight: 600;
            color: #409eff;
          }

          .unit {
            font-size: 14px;
            color: #909399;
            margin-left: 4px;
          }
        }

        .confidence {
          font-size: 12px;
          color: #909399;
          margin-top: 8px;
        }
      }
    }

    .prediction-row {
      display: flex;
      gap: 24px;
      margin-bottom: 16px;

      .prediction-item {
        flex: 1;

        .label {
          font-size: 12px;
          color: #909399;
          margin-bottom: 8px;
        }
      }
    }

    .recommendations {
      background: #f5f7fa;
      border-radius: 8px;
      padding: 12px 16px;

      .label {
        font-size: 12px;
        color: #606266;
        margin-bottom: 8px;
        font-weight: 500;
      }

      ul {
        margin: 0;
        padding-left: 16px;

        li {
          font-size: 13px;
          color: #606266;
          line-height: 1.6;
        }
      }
    }
  }

  .empty-state {
    padding: 40px 0;
  }
}
</style>
