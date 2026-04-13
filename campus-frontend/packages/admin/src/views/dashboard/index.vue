<template>
  <div class="dashboard-page">
    <!-- 实时统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="6" v-for="stat in statistics" :key="stat.label">
        <div class="stat-card" :class="{ 'pulse': stat.change !== 0 }">
          <div class="stat-icon" :style="{ background: stat.bgColor }">
            <el-icon size="24" :color="stat.color">
              <component :is="stat.icon" />
            </el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" :style="{ color: stat.color }">
              {{ stat.value }}
              <span v-if="stat.change !== 0" class="stat-change" :class="stat.change > 0 ? 'up' : 'down'">
                {{ stat.change > 0 ? '+' : '' }}{{ stat.change }}%
              </span>
            </div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-header">
            <h3>活动趋势</h3>
            <el-radio-group v-model="timeRange" size="small">
              <el-radio-button label="24h">24小时</el-radio-button>
              <el-radio-button label="7d">7天</el-radio-button>
              <el-radio-button label="30d">30天</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-body" ref="trendChartRef"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-header">
            <h3>社团活跃度排行</h3>
          </div>
          <div class="chart-body">
            <div class="club-ranking">
              <div v-for="(club, index) in clubRanking" :key="club.id" class="rank-item">
                <div class="rank-number" :class="{ 'top3': index < 3 }">{{ index + 1 }}</div>
                <div class="rank-info">
                  <div class="rank-name">{{ club.name }}</div>
                  <el-progress
                    :percentage="club.score"
                    :color="getProgressColor(index)"
                    :show-text="false"
                    :stroke-width="8"
                  />
                </div>
                <div class="rank-score">{{ club.score }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 待办事项和预警 -->
    <el-row :gutter="20" class="info-row">
      <el-col :xs="24" :lg="12">
        <div class="info-card">
          <div class="info-header">
            <h3>
              <el-icon><Bell /></el-icon>
              待办事项
            </h3>
            <el-badge :value="pendingCount" class="item" type="primary" />
          </div>
          <div class="info-body">
            <div v-for="item in pendingItems" :key="item.id" class="todo-item">
              <div class="todo-icon" :class="item.type">
                <el-icon><component :is="item.icon" /></el-icon>
              </div>
              <div class="todo-content">
                <div class="todo-title">{{ item.title }}</div>
                <div class="todo-time">{{ item.time }}</div>
              </div>
              <el-button type="primary" link size="small" @click="handleTodo(item)">
                处理
              </el-button>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="info-card alert">
          <div class="info-header">
            <h3>
              <el-icon><Warning /></el-icon>
              实时预警
            </h3>
          </div>
          <div class="info-body">
            <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="alert.level">
              <div class="alert-dot"></div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-desc">{{ alert.description }}</div>
              </div>
              <div class="alert-time">{{ alert.time }}</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import {
  Calendar, User, OfficeBuilding, Warning,
  Bell, DocumentChecked, CircleCheck
} from '@element-plus/icons-vue';

const router = useRouter();
const timeRange = ref('7d');
const trendChartRef = ref<HTMLElement>();

// 统计数据
const statistics = ref([
  { label: '今日活动', value: 12, change: 20, icon: Calendar, color: '#00d4aa', bgColor: 'rgba(0, 212, 170, 0.1)' },
  { label: '参与人数', value: 486, change: 15, icon: User, color: '#58a6ff', bgColor: 'rgba(88, 166, 255, 0.1)' },
  { label: '活跃社团', value: 28, change: 5, icon: OfficeBuilding, color: '#a371f7', bgColor: 'rgba(163, 113, 247, 0.1)' },
  { label: '待审批', value: 8, change: 0, icon: DocumentChecked, color: '#f0883e', bgColor: 'rgba(240, 136, 62, 0.1)' },
]);

// 社团排行
const clubRanking = ref([
  { id: 1, name: '科技创新社', score: 98 },
  { id: 2, name: '文艺社', score: 92 },
  { id: 3, name: '体育协会', score: 88 },
  { id: 4, name: '志愿者协会', score: 85 },
  { id: 5, name: '英语角', score: 78 },
]);

// 待办事项
const pendingCount = ref(8);
const pendingItems = ref([
  { id: 1, type: 'activity', icon: Calendar, title: '科技创新讲座活动审批', time: '10分钟前' },
  { id: 2, type: 'resource', icon: OfficeBuilding, title: '礼堂资源预约申请', time: '30分钟前' },
  { id: 3, type: 'activity', icon: Calendar, title: '编程工作坊活动审批', time: '1小时前' },
  { id: 4, type: 'resource', icon: OfficeBuilding, title: '运动场预约申请', time: '2小时前' },
]);

// 预警信息
const alerts = ref([
  { id: 1, level: 'warning', title: '资源利用率过高', description: '本周礼堂使用率超过90%', time: '5分钟前' },
  { id: 2, level: 'info', title: '大型活动即将开始', description: '科技创新讲座将在30分钟后开始', time: '10分钟前' },
  { id: 3, level: 'danger', title: '活动冲突警告', description: '检测到2个活动场地冲突', time: '15分钟前' },
]);

const getProgressColor = (index: number) => {
  const colors = ['#00d4aa', '#58a6ff', '#a371f7', '#f0883e', '#6e7681'];
  return colors[index] || '#6e7681';
};

const handleTodo = (item: any) => {
  if (item.type === 'activity') {
    router.push('/approval/pending');
  } else {
    router.push('/resource/allocation');
  }
};

onMounted(() => {
  // TODO: 初始化图表
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

  &.pulse {
    animation: pulse 2s infinite;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.9; }
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-change {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;

  &.up {
    background: rgba(0, 212, 170, 0.2);
    color: #00d4aa;
  }

  &.down {
    background: rgba(248, 81, 73, 0.2);
    color: #f85149;
  }
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

    &.alert {
      border-color: rgba(248, 81, 73, 0.3);
    }
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

  .todo-time {
    font-size: 12px;
    color: #6e7681;
    margin-top: 2px;
  }
}

.alert-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  background: #0d1117;
  border-radius: 8px;
  margin-bottom: 8px;
  border-left: 3px solid transparent;

  &.warning {
    border-left-color: #f0883e;
  }

  &.danger {
    border-left-color: #f85149;
  }

  &.info {
    border-left-color: #58a6ff;
  }

  .alert-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 12px;
    margin-top: 6px;
    flex-shrink: 0;

    .warning & {
      background: #f0883e;
    }

    .danger & {
      background: #f85149;
    }

    .info & {
      background: #58a6ff;
    }
  }

  .alert-content {
    flex: 1;
  }

  .alert-title {
    font-size: 14px;
    color: #c9d1d9;
  }

  .alert-desc {
    font-size: 12px;
    color: #6e7681;
    margin-top: 2px;
  }

  .alert-time {
    font-size: 12px;
    color: #484f58;
    flex-shrink: 0;
  }
}
</style>
