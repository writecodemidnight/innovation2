<template>
  <div class="global-report-page">
    <div class="page-header">
      <h2>全局报表</h2>
      <el-date-picker
        v-model="dateRange"
        type="monthrange"
        range-separator="至"
        start-placeholder="开始月份"
        end-placeholder="结束月份"
        value-format="YYYY-MM"
      />
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="stat in statistics" :key="stat.label">
        <el-card class="stat-card">
          <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-change" :class="stat.change > 0 ? 'up' : 'down'">
            {{ stat.change > 0 ? '+' : '' }}{{ stat.change }}% 环比
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>活动趋势</span>
          </template>
          <div ref="activityTrendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>社团活跃度排行</span>
          </template>
          <div ref="clubRankingChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>活动类型分布</span>
          </template>
          <div ref="activityTypeChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>资源利用率</span>
          </template>
          <div ref="resourceUtilChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>
        <div class="table-header">
          <span>详细数据</span>
          <el-button type="primary" @click="handleExport">导出Excel</el-button>
        </div>
      </template>
      <el-table :data="tableData" style="width: 100%">
        <el-table-column prop="month" label="月份" width="100" />
        <el-table-column prop="activityCount" label="活动数" width="100" />
        <el-table-column prop="participantCount" label="参与人次" width="120" />
        <el-table-column prop="avgRating" label="平均评分" width="100" />
        <el-table-column prop="resourceUtilization" label="资源利用率" width="120" />
        <el-table-column prop="topClub" label="最活跃社团" min-width="150" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const dateRange = ref([]);
const statistics = ref([
  { label: '总活动数', value: 156, change: 12, color: '#409eff' },
  { label: '参与人次', value: 3280, change: 8, color: '#67c23a' },
  { label: '活跃社团', value: 28, change: 5, color: '#e6a23c' },
  { label: '平均评分', value: 4.5, change: 3, color: '#f56c6c' },
]);

const activityTrendChart = ref<HTMLElement>();
const clubRankingChart = ref<HTMLElement>();
const activityTypeChart = ref<HTMLElement>();
const resourceUtilChart = ref<HTMLElement>();

const tableData = ref([
  {
    month: '2024-03',
    activityCount: 45,
    participantCount: 980,
    avgRating: 4.6,
    resourceUtilization: '85%',
    topClub: '科技创新社',
  },
  {
    month: '2024-02',
    activityCount: 38,
    participantCount: 850,
    avgRating: 4.5,
    resourceUtilization: '78%',
    topClub: '文艺社',
  },
]);

function handleExport() {
  ElMessage.success('导出成功');
}

onMounted(() => {
  // TODO: 初始化图表
});
</script>

<style scoped lang="scss">
.global-report-page {
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

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;

  .stat-value {
    font-size: 32px;
    font-weight: 700;
  }

  .stat-label {
    margin-top: 8px;
    color: #666;
  }

  .stat-change {
    margin-top: 8px;
    font-size: 13px;

    &.up {
      color: #67c23a;
    }

    &.down {
      color: #f56c6c;
    }
  }
}

.chart-row {
  margin-bottom: 24px;
}

.chart-container {
  height: 300px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
