<template>
  <div class="dashboard-page">
    <!-- 实时统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(0, 212, 170, 0.1)">
            <el-icon size="24" color="#00d4aa"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #00d4aa">{{ stats?.totalClubs || 0 }}</div>
            <div class="stat-label">社团总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(88, 166, 255, 0.1)">
            <el-icon size="24" color="#58a6ff"><Calendar /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #58a6ff">{{ stats?.totalActivities || 0 }}</div>
            <div class="stat-label">活动总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(163, 113, 247, 0.1)">
            <el-icon size="24" color="#a371f7"><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #a371f7">{{ stats?.totalUsers || 0 }}</div>
            <div class="stat-label">用户总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card" @click="goToPending" style="cursor: pointer">
          <div class="stat-icon" style="background: rgba(240, 136, 62, 0.1)">
            <el-icon size="24" color="#f0883e"><DocumentChecked /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #f0883e">{{ pendingTotal || 0 }}</div>
            <div class="stat-label">待审批</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-header">
            <h3>活动趋势（最近7天）</h3>
          </div>
          <div class="chart-body" ref="trendChartRef" v-loading="loading"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-header">
            <h3>社团活跃度排行</h3>
          </div>
          <div class="chart-body" v-loading="loading">
            <div class="club-ranking" v-if="clubRankings.length > 0">
              <div v-for="(club, index) in clubRankings" :key="club.id" class="rank-item">
                <div class="rank-number" :class="{ 'top3': index < 3 }">{{ index + 1 }}</div>
                <div class="rank-info">
                  <div class="rank-name">{{ club.name }}</div>
                  <el-progress
                    :percentage="Math.min(club.score, 100)"
                    :color="getProgressColor(index)"
                    :show-text="false"
                    :stroke-width="8"
                  />
                </div>
                <div class="rank-score">{{ club.score }}</div>
              </div>
            </div>
            <el-empty v-else description="暂无数据" />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 资源使用和待办 -->
    <el-row :gutter="20" class="info-row">
      <el-col :xs="24" :lg="12">
        <div class="info-card">
          <div class="info-header">
            <h3>
              <el-icon><OfficeBuilding /></el-icon>
              资源使用情况
            </h3>
          </div>
          <div class="info-body" v-loading="loading">
            <div class="resource-stats" v-if="resourceUsage">
              <div class="resource-item">
                <span class="resource-label">场地</span>
                <el-progress
                  :percentage="resourceUsage.typeDistribution['场地'] || 0"
                  color="#00d4aa"
                />
              </div>
              <div class="resource-item">
                <span class="resource-label">设备</span>
                <el-progress
                  :percentage="resourceUsage.typeDistribution['设备'] || 0"
                  color="#58a6ff"
                />
              </div>
              <div class="resource-item">
                <span class="resource-label">会议室</span>
                <el-progress
                  :percentage="resourceUsage.typeDistribution['会议室'] || 0"
                  color="#a371f7"
                />
              </div>
              <div class="utilization-rate">
                <span>资源利用率</span>
                <span class="rate-value">{{ resourceUsage.utilizationRate }}%</span>
              </div>
            </div>
            <el-empty v-else description="暂无数据" />
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="info-card">
          <div class="info-header">
            <h3>
              <el-icon><Bell /></el-icon>
              待办事项
            </h3>
            <el-badge :value="pendingTasks?.total || 0" class="item" type="primary" />
          </div>
          <div class="info-body" v-loading="loading">
            <div v-if="pendingTasks">
              <div class="todo-item" v-if="pendingTasks.activityApprovals > 0">
                <div class="todo-icon activity">
                  <el-icon><Calendar /></el-icon>
                </div>
                <div class="todo-content">
                  <div class="todo-title">活动审批</div>
                  <div class="todo-count">{{ pendingTasks.activityApprovals }} 个待审批</div>
                </div>
                <el-button type="primary" link size="small" @click="goToPending">
                  去处理
                </el-button>
              </div>
              <div class="todo-item" v-if="pendingTasks.fundApprovals > 0">
                <div class="todo-icon fund">
                  <el-icon><Money /></el-icon>
                </div>
                <div class="todo-content">
                  <div class="todo-title">资金审批</div>
                  <div class="todo-count">{{ pendingTasks.fundApprovals }} 个待审批</div>
                </div>
                <el-button type="primary" link size="small" @click="goToPending">
                  去处理
                </el-button>
              </div>
              <div class="todo-item" v-if="pendingTasks.resourceBookings > 0">
                <div class="todo-icon resource">
                  <el-icon><OfficeBuilding /></el-icon>
                </div>
                <div class="todo-content">
                  <div class="todo-title">资源预约审批</div>
                  <div class="todo-count">{{ pendingTasks.resourceBookings }} 个待审批</div>
                </div>
                <el-button type="primary" link size="small" @click="goToPending">
                  去处理
                </el-button>
              </div>
              <el-empty v-if="pendingTasks.total === 0" description="暂无待办事项" />
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import {
  Calendar, User, OfficeBuilding, DocumentChecked, Bell, Money
} from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import { useDashboardStore, useApprovalStore } from '@/stores';

const router = useRouter();
const dashboardStore = useDashboardStore();
const approvalStore = useApprovalStore();

const loading = computed(() => dashboardStore.loading);
const stats = computed(() => dashboardStore.stats);
const clubRankings = computed(() => dashboardStore.clubRankings);
const resourceUsage = computed(() => dashboardStore.resourceUsage);
const pendingTasks = computed(() => dashboardStore.pendingTasks);
const pendingTotal = computed(() => approvalStore.totalPending);

const trendChartRef = ref<HTMLElement>();
let trendChart: echarts.ECharts | null = null;

const getProgressColor = (index: number) => {
  const colors = ['#00d4aa', '#58a6ff', '#a371f7', '#f0883e', '#6e7681'];
  return colors[index] || '#6e7681';
};

const goToPending = () => {
  router.push('/approval/pending');
};

// 初始化趋势图
const initTrendChart = () => {
  if (!trendChartRef.value) return;

  trendChart = echarts.init(trendChartRef.value);
  updateTrendChart();
};

// 更新趋势图数据
const updateTrendChart = () => {
  if (!trendChart) return;

  const trends = dashboardStore.activityTrends;
  const dates = trends.map(t => t.date.slice(5)); // 显示 MM-DD
  const counts = trends.map(t => t.count);

  const option = {
    tooltip: {
      trigger: 'axis',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: dates.length > 0 ? dates : ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: {
        lineStyle: {
          color: '#30363d',
        },
      },
      axisLabel: {
        color: '#8b949e',
      },
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#30363d',
        },
      },
      axisLabel: {
        color: '#8b949e',
      },
      splitLine: {
        lineStyle: {
          color: '#21262d',
        },
      },
    },
    series: [
      {
        name: '活动数',
        type: 'line',
        smooth: true,
        data: counts.length > 0 ? counts : [0, 0, 0, 0, 0, 0, 0],
        lineStyle: {
          color: '#00d4aa',
          width: 3,
        },
        areaStyle: {
          color: new (echarts as any).graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 170, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 170, 0.05)' },
          ]),
        },
        itemStyle: {
          color: '#00d4aa',
        },
      },
    ],
  };
  trendChart.setOption(option);
};

// 监听窗口大小变化
const handleResize = () => {
  trendChart?.resize();
};

onMounted(async () => {
  // 加载所有数据
  await Promise.all([
    dashboardStore.loadAllDashboardData(),
    approvalStore.fetchApprovalCounts(),
  ]);

  // 初始化图表
  initTrendChart();
  updateTrendChart();

  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  trendChart?.dispose();
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped lang="scss">
.dashboard-page {
  color: #c9d1d9;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  transition: all 0.3s;

  &:hover {
    border-color: #58a6ff;
    transform: translateY(-2px);
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #8b949e;
  margin-top: 4px;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 20px;
  height: 400px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h3 {
    font-size: 16px;
    color: #fff;
    margin: 0;
  }
}

.chart-body {
  height: calc(100% - 50px);
}

.club-ranking {
  .rank-item {
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #21262d;

    &:last-child {
      border-bottom: none;
    }
  }

  .rank-number {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    background: #21262d;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 600;
    margin-right: 12px;

    &.top3 {
      background: #238636;
      color: #fff;
    }
  }

  .rank-info {
    flex: 1;
  }

  .rank-name {
    font-size: 14px;
    color: #c9d1d9;
    margin-bottom: 8px;
  }

  .rank-score {
    font-size: 16px;
    font-weight: 600;
    color: #00d4aa;
    margin-left: 12px;
  }
}

.info-row {
  .info-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
  }
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h3 {
    font-size: 16px;
    color: #fff;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.resource-stats {
  .resource-item {
    display: flex;
    align-items: center;
    margin-bottom: 16px;

    .resource-label {
      width: 60px;
      color: #8b949e;
    }

    .el-progress {
      flex: 1;
    }
  }

  .utilization-rate {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 16px;
    border-top: 1px solid #21262d;
    margin-top: 16px;

    .rate-value {
      font-size: 24px;
      font-weight: 700;
      color: #00d4aa;
    }
  }
}

.todo-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #0d1117;
  border-radius: 8px;
  margin-bottom: 8px;

  .todo-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 12px;

    &.activity {
      background: rgba(0, 212, 170, 0.1);
      color: #00d4aa;
    }

    &.fund {
      background: rgba(163, 113, 247, 0.1);
      color: #a371f7;
    }

    &.resource {
      background: rgba(88, 166, 255, 0.1);
      color: #58a6ff;
    }
  }

  .todo-content {
    flex: 1;
  }

  .todo-title {
    font-size: 14px;
    color: #c9d1d9;
  }

  .todo-count {
    font-size: 12px;
    color: #6e7681;
    margin-top: 2px;
  }
}
</style>
