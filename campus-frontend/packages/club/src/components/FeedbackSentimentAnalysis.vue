<template>
  <el-card class="feedback-analysis">
    <template #header>
      <div class="card-header">
        <span>反馈情感分析</span>
        <el-tag size="small" type="success">AI</el-tag>
      </div>
    </template>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="analysis" class="analysis-content">
      <!-- 总体评分 -->
      <div class="score-section">
        <div class="score-circle" :class="getScoreClass(analysis.average_score)">
          <span class="score">{{ formatScore(analysis.average_score) }}</span>
          <span class="label">综合评分</span>
        </div>
      </div>

      <!-- 情感分布 -->
      <div class="distribution">
        <div class="dist-item positive">
          <el-icon><SuccessFilled /></el-icon>
          <span class="count">{{ analysis.positive_count }}</span>
          <span class="label">正面</span>
        </div>
        <div class="dist-item neutral">
          <el-icon><InfoFilled /></el-icon>
          <span class="count">{{ analysis.neutral_count }}</span>
          <span class="label">中性</span>
        </div>
        <div class="dist-item negative">
          <el-icon><CircleCloseFilled /></el-icon>
          <span class="count">{{ analysis.negative_count }}</span>
          <span class="label">负面</span>
        </div>
      </div>

      <!-- 总反馈数 -->
      <div class="total-feedback">
        共 {{ analysis.total_feedback }} 条反馈
      </div>

      <!-- 关键词云 -->
      <div v-if="analysis.keywords?.length" class="keywords">
        <div class="label">关键词</div>
        <div class="tag-cloud">
          <el-tag
            v-for="(keyword, index) in analysis.keywords"
            :key="index"
            :type="getKeywordType(index)"
            size="small"
            class="keyword-tag"
          >
            {{ keyword }}
          </el-tag>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <el-empty description="暂无分析数据" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { analyzeFeedback } from '@/api/algorithm';
import { ElMessage } from 'element-plus';
import { SuccessFilled, InfoFilled, CircleCloseFilled } from '@element-plus/icons-vue';

interface FeedbackItem {
  studentId: string;
  text: string;
}

interface AnalysisResult {
  average_score: number;
  positive_count: number;
  neutral_count: number;
  negative_count: number;
  total_feedback: number;
  keywords?: string[];
}

const props = defineProps<{
  activityId: string;
  feedbacks: FeedbackItem[];
}>();

const loading = ref(false);
const analysis = ref<AnalysisResult | null>(null);

const getScoreClass = (score: number) => {
  if (score >= 0.7) return 'excellent';
  if (score >= 0.5) return 'good';
  return 'poor';
};

const formatScore = (score: number) => {
  return Math.round(score * 100);
};

const getKeywordType = (index: number) => {
  const types = ['success', 'warning', 'info', 'danger'] as const;
  return types[index % types.length];
};

const loadAnalysis = async () => {
  if (!props.feedbacks?.length) {
    return;
  }

  loading.value = true;
  try {
    const response = await analyzeFeedback({
      activityId: props.activityId,
      feedbacks: props.feedbacks,
    });
    analysis.value = response as AnalysisResult;
  } catch (error: any) {
    ElMessage.error('情感分析失败');
    console.error('Analysis error:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadAnalysis();
});
</script>

<style scoped lang="scss">
.feedback-analysis {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .loading-state {
    padding: 20px 0;
  }

  .analysis-content {
    .score-section {
      display: flex;
      justify-content: center;
      padding: 20px 0;

      .score-circle {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 4px solid;

        &.excellent {
          border-color: #67c23a;
          background: #f0f9eb;

          .score {
            color: #67c23a;
          }
        }

        &.good {
          border-color: #e6a23c;
          background: #fdf6ec;

          .score {
            color: #e6a23c;
          }
        }

        &.poor {
          border-color: #f56c6c;
          background: #fef0f0;

          .score {
            color: #f56c6c;
          }
        }

        .score {
          font-size: 28px;
          font-weight: 600;
        }

        .label {
          font-size: 12px;
          color: #606266;
          margin-top: 4px;
        }
      }
    }

    .distribution {
      display: flex;
      justify-content: space-around;
      padding: 16px 0;
      border-top: 1px solid #ebeef5;
      border-bottom: 1px solid #ebeef5;

      .dist-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;

        .el-icon {
          font-size: 24px;
        }

        &.positive .el-icon {
          color: #67c23a;
        }

        &.neutral .el-icon {
          color: #909399;
        }

        &.negative .el-icon {
          color: #f56c6c;
        }

        .count {
          font-size: 20px;
          font-weight: 600;
        }

        .label {
          font-size: 12px;
          color: #909399;
        }
      }
    }

    .total-feedback {
      text-align: center;
      padding: 12px 0;
      font-size: 13px;
      color: #606266;
    }

    .keywords {
      padding-top: 12px;
      border-top: 1px solid #ebeef5;

      .label {
        font-size: 12px;
        color: #606266;
        margin-bottom: 8px;
      }

      .tag-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .keyword-tag {
          margin: 0;
        }
      }
    }
  }

  .empty-state {
    padding: 40px 0;
  }
}
</style>
