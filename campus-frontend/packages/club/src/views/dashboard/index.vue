<template>
  <div class="dashboard-page">
    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stat-cards">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" v-loading="statsLoading">
          <div class="stat-icon" style="background: #e6f7ff;">
            <el-icon size="32" color="#1890ff"><Calendar /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.monthlyActivities }}</div>
            <div class="stat-label">本月活动</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" v-loading="statsLoading">
          <div class="stat-icon" style="background: #f6ffed;">
            <el-icon size="32" color="#52c41a"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalParticipants }}</div>
            <div class="stat-label">参与人次</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" v-loading="statsLoading">
          <div class="stat-icon" style="background: #fff7e6;">
            <el-icon size="32" color="#fa8c16"><Star /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.averageRating.toFixed(1) }}</div>
            <div class="stat-label">平均评分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card" v-loading="statsLoading">
          <div class="stat-icon" style="background: #f9f0ff;">
            <el-icon size="32" color="#722ed1"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.resourceUtilizationRate.toFixed(0) }}%</div>
            <div class="stat-label">资源利用率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="24" class="chart-row">
      <el-col :xs="24" :lg="16">
        <el-card title="活动趋势">
          <template #header>
            <div class="card-header">
              <span>活动趋势</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button value="week">本周</el-radio-button>
                <el-radio-button value="month">本月</el-radio-button>
                <el-radio-button value="year">本年</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="trendChartRef"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>活动类型分布</span>
            </div>
          </template>
          <div class="chart-container" ref="pieChartRef"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-card class="recent-activities">
      <template #header>
        <div class="card-header">
          <span>最近活动</span>
          <el-button type="primary" text @click="$router.push('/activities')">
            查看全部
          </el-button>
        </div>
      </template>
      <el-table :data="recentActivities" style="width: 100%">
        <el-table-column prop="title" label="活动名称" min-width="200" />
        <el-table-column prop="startTime" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.startTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="participants" label="报名人数" width="120">
          <template #default="{ row }">
            {{ row.currentParticipants }}/{{ row.maxParticipants }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row.id)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { Calendar, User, Star, TrendCharts } from '@element-plus/icons-vue';
import { formatDateTime, ActivityStatusMap, ActivityStatus } from '@campus/shared';
import type { Activity, ClubDashboardStats } from '@campus/shared';
import * as echarts from 'echarts';
import { activityApi } from '@/api/activity';
import { dashboardApi } from '@/api/dashboard';
import { ElMessage } from 'element-plus';

const router = useRouter();
const trendPeriod = ref('month');
const trendChartRef = ref<HTMLElement>();
const pieChartRef = ref<HTMLElement>();
const statsLoading = ref(false);

// 统计数据
const stats = ref<ClubDashboardStats>({
  monthlyActivities: 0,
  monthlyGrowthRate: 0,
  totalParticipants: 0,
  averageRating: 0,
  resourceUtilizationRate: 0,
  pendingApprovals: 0,
  ongoingActivities: 0,
  completedActivities: 0,
});

// 最近活动数据
const recentActivities = ref<Partial<Activity>[]>([]);

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    REGISTERING: 'success',
    PENDING_APPROVAL: 'warning',
    COMPLETED: 'info',
    CANCELLED: 'danger',
  };
  return map[status] || 'info';
};

const getStatusLabel = (status: string) => {
  return ActivityStatusMap[status as ActivityStatus]?.label || status;
};

const viewDetail = (id: number) => {
  router.push(`/activities/${id}`);
};

// 加载统计数据
const loadStats = async () => {
  statsLoading.value = true;
  try {
    const response = await dashboardApi.getStats();
    stats.value = response;
  } catch (error: any) {
    ElMessage.error(error.message || '获取统计数据失败');
  } finally {
    statsLoading.value = false;
  }
};

// 图表实例
let trendChart: echarts.ECharts | null = null;
let pieChart: echarts.ECharts | null = null;

// 初始化趋势图
const initTrendChart = () => {
  if (!trendChartRef.value) return;

  trendChart = echarts.init(trendChartRef.value);
  const option = {
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '活动数',
        type: 'line',
        smooth: true,
        data: [2, 3, 1, 4, 2, 5, 3],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
            { offset: 1, color: 'rgba(24, 144, 255, 0.05)' },
          ]),
        },
        lineStyle: {
          color: '#1890ff',
        },
        itemStyle: {
          color: '#1890ff',
        },
      },
    ],
  };
  trendChart.setOption(option);
};

// 初始化饼图
const initPieChart = () => {
  if (!pieChartRef.value) return;

  pieChart = echarts.init(pieChartRef.value);
  const option = {
    tooltip: {
      trigger: 'item',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '活动类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
          },
        },
        labelLine: {
          show: false,
        },
        data: [
          { value: 12, name: '讲座' },
          { value: 8, name: '工作坊' },
          { value: 5, name: '竞赛' },
          { value: 3, name: '社交' },
          { value: 2, name: '其他' },
        ],
      },
    ],
  };
  pieChart.setOption(option);
};

// 加载最近活动
const loadRecentActivities = async () => {
  try {
    const response = await activityApi.getList({ page: 0, size: 5 });
    recentActivities.value = response.content || [];
  } catch (error) {
    // 使用默认数据
  }
};

onMounted(() => {
  initTrendChart();
  initPieChart();
  loadStats();
  loadRecentActivities();

  // 窗口大小改变时重绘图表
  window.addEventListener('resize', () => {
    trendChart?.resize();
    pieChart?.resize();
  });
});

onUnmounted(() => {
  trendChart?.dispose();
  pieChart?.dispose();
  window.removeEventListener('resize', () => {
    trendChart?.resize();
    pieChart?.resize();
  });
});
</script>

<style scoped lang="scss">
.dashboard-page {
  .stat-cards {
    margin-bottom: 24px;
  }

  .stat-card {
    :deep(.el-card__body) {
      display: flex;
      align-items: center;
      padding: 20px;
    }

    .stat-icon {
      width: 64px;
      height: 64px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16px;
    }

    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      line-height: 1.2;
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-top: 4px;
    }
  }

  .chart-row {
    margin-bottom: 24px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .chart-container {
    height: 300px;
  }

  .recent-activities {
    :deep(.el-card__body) {
      padding: 0;
    }
  }
}
</style>
