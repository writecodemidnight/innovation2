<template>
  <div class="report-radar-page">
    <div class="page-header">
      <h2>活动效果分析</h2>
      <el-select
        v-model="selectedActivityId"
        placeholder="选择活动"
        style="width: 300px"
        :loading="activityLoading"
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
      <el-col :span="12">
        <el-card v-loading="chartLoading">
          <template #header>
            <span>五维评估雷达图</span>
          </template>
          <v-chart ref="radarChartRef" class="chart-container" :option="radarOption" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card v-loading="detailLoading">
          <template #header>
            <span>评估详情</span>
          </template>
          <div v-if="evaluationData" class="evaluation-details">
            <div v-for="(item, index) in evaluationItems" :key="index" class="evaluation-item">
              <div class="item-header">
                <span class="item-name">{{ item.name }}</span>
                <span class="item-score">{{ item.score }}分</span>
              </div>
              <el-progress :percentage="item.score" :color="getScoreColor(item.score)" />
              <div class="item-desc">{{ item.description }}</div>
            </div>
          </div>
          <el-empty v-else description="暂无评估数据" />
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="evaluationData" class="summary-card">
      <template #header>
        <span>综合评价</span>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="总评分">{{ evaluationData.totalScore }}分</el-descriptions-item>
        <el-descriptions-item label="参与人数">{{ evaluationData.participantCount }}人</el-descriptions-item>
        <el-descriptions-item label="评价人数">{{ evaluationData.evaluationCount }}人</el-descriptions-item>
        <el-descriptions-item label="优点" :span="3">{{ evaluationData.strengths || '暂无数据' }}</el-descriptions-item>
        <el-descriptions-item label="改进建议" :span="3">{{ evaluationData.improvementSuggestions?.join('；') || '暂无数据' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { RadarChart } from 'echarts/charts';
import { TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import { ElMessage } from 'element-plus';
import { activityApi } from '@/api/activity';
import type { Activity, ActivityEvaluationReport } from '@campus/shared';

// 注册 ECharts 组件
use([CanvasRenderer, RadarChart, TooltipComponent, LegendComponent, TitleComponent]);

const selectedActivityId = ref<number | undefined>(undefined);
const activities = ref<Activity[]>([]);
const evaluationData = ref<ActivityEvaluationReport | null>(null);
const activityLoading = ref(false);
const chartLoading = ref(false);
const detailLoading = ref(false);

// 评估项配置
const dimensionConfig = [
  { key: 'participation', name: '参与度', description: '学生参与程度，包括到场率、互动积极性等' },
  { key: 'educational', name: '教育性', description: '活动的教育价值和学习效果' },
  { key: 'innovation', name: '创新性', description: '活动形式和内容的新颖程度' },
  { key: 'influence', name: '影响力', description: '活动在校园内外的传播和影响' },
  { key: 'sustainability', name: '可持续性', description: '活动组织的规范性和可复制性' },
];

// 计算评估项数据
const evaluationItems = computed(() => {
  if (!evaluationData.value) return [];
  const dims = evaluationData.value.dimensions;
  return dimensionConfig.map(config => ({
    name: config.name,
    score: Math.round(dims[config.key as keyof typeof dims] || 0),
    description: config.description,
  }));
});

// 雷达图配置
const radarOption = computed(() => {
  if (!evaluationData.value) return {};

  const dims = evaluationData.value.dimensions;
  const data = dimensionConfig.map(config => dims[config.key as keyof typeof dims] || 0);

  return {
    title: {
      text: evaluationData.value.activityTitle,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal',
      },
    },
    tooltip: {
      trigger: 'item',
    },
    radar: {
      indicator: dimensionConfig.map(config => ({
        name: config.name,
        max: 100,
      })),
      radius: '65%',
      center: ['50%', '55%'],
      splitNumber: 4,
      axisName: {
        color: '#666',
        fontSize: 12,
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(64, 158, 255, 0.2)',
        },
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(64, 158, 255, 0.05)', 'rgba(64, 158, 255, 0.1)',
                  'rgba(64, 158, 255, 0.15)', 'rgba(64, 158, 255, 0.2)'],
        },
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(64, 158, 255, 0.3)',
        },
      },
    },
    series: [{
      type: 'radar',
      data: [{
        value: data,
        name: '活动评分',
        areaStyle: {
          color: 'rgba(64, 158, 255, 0.3)',
        },
        lineStyle: {
          color: '#409eff',
          width: 2,
        },
        itemStyle: {
          color: '#409eff',
        },
      }],
    }],
  };
});

// 加载活动列表
async function loadActivities() {
  activityLoading.value = true;
  try {
    const response = await activityApi.getList({
      page: 0,
      size: 100,
    });
    activities.value = response.content || [];
    // 如果有活动且未选择，自动选择第一个
    if (activities.value.length > 0 && !selectedActivityId.value) {
      selectedActivityId.value = activities.value[0].id;
      await loadEvaluationData(activities.value[0].id);
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取活动列表失败');
  } finally {
    activityLoading.value = false;
  }
}

// 加载评估数据
async function loadEvaluationData(activityId: number) {
  chartLoading.value = true;
  detailLoading.value = true;
  try {
    const data = await activityApi.getEvaluationReport(activityId);
    evaluationData.value = data;
  } catch (error: any) {
    ElMessage.error(error.message || '获取评估数据失败');
    evaluationData.value = null;
  } finally {
    chartLoading.value = false;
    detailLoading.value = false;
  }
}

// 活动选择变化
async function handleActivityChange(activityId: number) {
  if (activityId) {
    await loadEvaluationData(activityId);
  }
}

// 获取分数颜色
function getScoreColor(score: number) {
  if (score >= 90) return '#67c23a';
  if (score >= 80) return '#409eff';
  if (score >= 60) return '#e6a23c';
  return '#f56c6c';
}

onMounted(() => {
  loadActivities();
});
</script>

<style scoped lang="scss">
.report-radar-page {
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

.chart-container {
  height: 400px;
}

.evaluation-details {
  .evaluation-item {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .item-name {
      font-weight: 500;
    }

    .item-score {
      font-size: 18px;
      font-weight: 600;
      color: #409eff;
    }
  }

  .item-desc {
    margin-top: 8px;
    font-size: 13px;
    color: #666;
  }
}

.summary-card {
  margin-top: 24px;
}
</style>
