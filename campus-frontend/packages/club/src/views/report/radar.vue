<template>
  <div class="report-radar-page">
    <div class="page-header">
      <h2>活动效果分析</h2>
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
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>五维评估雷达图</span>
          </template>
          <div ref="radarChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>评估详情</span>
          </template>
          <div class="evaluation-details">
            <div v-for="(item, index) in evaluationItems" :key="index" class="evaluation-item">
              <div class="item-header">
                <span class="item-name">{{ item.name }}</span>
                <span class="item-score">{{ item.score }}分</span>
              </div>
              <el-progress :percentage="item.score" :color="getScoreColor(item.score)" />
              <div class="item-desc">{{ item.description }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="summary-card">
      <template #header>
        <span>综合评价</span>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="总评分">{{ totalScore }}分</el-descriptions-item>
        <el-descriptions-item label="参与人数">{{ participantCount }}人</el-descriptions-item>
        <el-descriptions-item label="评价人数">{{ evaluatorCount }}人</el-descriptions-item>
        <el-descriptions-item label="优点" :span="3">{{ strengths }}</el-descriptions-item>
        <el-descriptions-item label="改进建议" :span="3">{{ suggestions }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const selectedActivity = ref('');
const radarChartRef = ref<HTMLElement>();

const activities = ref([
  { id: 1, title: '科技创新讲座' },
  { id: 2, title: '编程工作坊' },
]);

const evaluationItems = ref([
  { name: '参与度', score: 85, description: '活动参与积极性较高，现场互动良好' },
  { name: '教育性', score: 90, description: '内容充实，对参与者有较大帮助' },
  { name: '创新性', score: 75, description: '活动形式较为新颖，但仍有提升空间' },
  { name: '影响力', score: 80, description: '在校园内产生一定影响力' },
  { name: '可持续性', score: 88, description: '活动组织有序，可持续开展' },
]);

const totalScore = ref(83.6);
const participantCount = ref(86);
const evaluatorCount = ref(52);
const strengths = ref('活动内容丰富，专家讲解深入浅出，现场互动环节设计合理，参与者反馈积极。');
const suggestions = ref('建议增加实践环节，延长互动时间；提前宣传，扩大活动影响力；做好后续跟进。');

function getScoreColor(score: number) {
  if (score >= 90) return '#67c23a';
  if (score >= 80) return '#409eff';
  if (score >= 60) return '#e6a23c';
  return '#f56c6c';
}

onMounted(() => {
  // TODO: 初始化 ECharts 雷达图
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
