<template>
  <div class="resource-calendar-page">
    <div class="page-header">
      <h2>资源预约日历</h2>
      <el-button type="primary" @click="handleApply">
        <el-icon><Plus /></el-icon>
        预约资源
      </el-button>
    </div>

    <!-- 资源筛选 -->
    <div class="filter-bar">
      <el-select
        v-model="selectedResource"
        placeholder="选择资源"
        clearable
        style="width: 200px"
        @change="handleResourceChange"
      >
        <el-option
          v-for="resource in resourceStore.resources"
          :key="resource.id"
          :label="resource.name"
          :value="resource.id"
        />
      </el-select>
      <el-button type="primary" link @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 日历视图 -->
    <el-card v-loading="loading">
      <el-calendar v-model="currentDate">
        <template #date-cell="{ data }">
          <div class="calendar-cell" @click="handleDateClick(data.day)">
            <div class="date-number">{{ data.day.split('-').slice(2).join('') }}</div>
            <div v-if="getReservationsByDate(data.day).length > 0" class="reservation-dots">
              <span
                v-for="res in getReservationsByDate(data.day).slice(0, 3)"
                :key="res.id"
                class="dot"
                :class="res.status"
              />
            </div>
            <div v-if="getReservationsByDate(data.day).length > 0" class="reservation-count">
              {{ getReservationsByDate(data.day).length }}个预约
            </div>
          </div>
        </template>
      </el-calendar>
    </el-card>

    <!-- 预约详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="预约详情" width="600px">
      <el-empty v-if="selectedDateReservations.length === 0" description="该日暂无预约" />
      <el-timeline v-else>
        <el-timeline-item
          v-for="res in selectedDateReservations"
          :key="res.id"
          :type="getTimelineType(res.status)"
          :timestamp="formatTimeRange(res.startTime, res.endTime)"
        >
          <h4>{{ res.resourceName }}</h4>
          <p>活动：{{ res.activityTitle }}</p>
          <p>
            状态：
            <el-tag :type="getStatusType(res.status)">{{ getStatusLabel(res.status) }}</el-tag>
          </p>
          <p v-if="res.purpose">备注：{{ res.purpose }}</p>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Plus, Refresh } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { useResourceStore } from '@/stores/resource';
import { formatDateTime } from '@campus/shared';
import type { ResourceReservation } from '@campus/shared';

const router = useRouter();
const resourceStore = useResourceStore();
const currentDate = ref(new Date());
const selectedResource = ref<number | undefined>(undefined);
const dialogVisible = ref(false);
const selectedDateReservations = ref<ResourceReservation[]>([]);
const loading = ref(false);

// 所有预约数据
const allReservations = ref<ResourceReservation[]>([]);

// 加载资源列表
async function loadResources() {
  try {
    await resourceStore.fetchResources();
  } catch (error: any) {
    ElMessage.error(error.message || '获取资源列表失败');
  }
}

// 加载所有预约
async function loadReservations() {
  loading.value = true;
  try {
    await resourceStore.fetchMyReservations();
    allReservations.value = resourceStore.reservations || [];
  } catch (error: any) {
    ElMessage.error(error.message || '获取预约列表失败');
    // 使用模拟数据
    allReservations.value = [
      {
        id: 1,
        resourceId: 1,
        resourceName: '学生活动中心301报告厅',
        activityTitle: '科技创新讲座',
        startTime: new Date().toISOString().split('T')[0] + 'T14:00:00',
        endTime: new Date().toISOString().split('T')[0] + 'T16:00:00',
        status: 'APPROVED',
        purpose: '需要投影仪和音响设备',
      },
      {
        id: 2,
        resourceId: 2,
        resourceName: '学生活动中心302会议室',
        activityTitle: '社团例会',
        startTime: new Date(Date.now() + 86400000).toISOString().split('T')[0] + 'T18:00:00',
        endTime: new Date(Date.now() + 86400000).toISOString().split('T')[0] + 'T20:00:00',
        status: 'PENDING',
      },
    ];
  } finally {
    loading.value = false;
  }
}

// 根据日期获取预约
function getReservationsByDate(dateStr: string) {
  let reservations = allReservations.value.filter(r => r.startTime.startsWith(dateStr));
  if (selectedResource.value) {
    reservations = reservations.filter(r => r.resourceId === selectedResource.value);
  }
  return reservations;
}

// 处理日期点击
function handleDateClick(dateStr: string) {
  selectedDateReservations.value = getReservationsByDate(dateStr);
  dialogVisible.value = true;
}

// 处理资源筛选变化
function handleResourceChange() {
  // 筛选变化时重新渲染日历
}

// 刷新数据
function refreshData() {
  loadReservations();
}

// 跳转预约页面
function handleApply() {
  router.push('/resources/apply');
}

// 格式化时间范围
function formatTimeRange(start: string, end: string) {
  const s = new Date(start).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  const e = new Date(end).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  return `${s} - ${e}`;
}

// 获取时间线类型
function getTimelineType(status: string) {
  const map: Record<string, any> = {
    APPROVED: 'primary',
    PENDING: 'warning',
    REJECTED: 'danger',
    CANCELLED: 'info',
  };
  return map[status] || 'info';
}

// 获取状态标签类型
function getStatusType(status: string) {
  const map: Record<string, any> = {
    APPROVED: 'success',
    PENDING: 'warning',
    REJECTED: 'danger',
    CANCELLED: 'info',
  };
  return map[status] || 'info';
}

// 获取状态标签文本
function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    APPROVED: '已通过',
    PENDING: '审核中',
    REJECTED: '已拒绝',
    CANCELLED: '已取消',
  };
  return map[status] || status;
}

onMounted(() => {
  Promise.all([loadResources(), loadReservations()]);
});
</script>

<style scoped lang="scss">
.resource-calendar-page {
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

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.calendar-cell {
  height: 100%;
  min-height: 60px;
  cursor: pointer;
  padding: 4px;

  &:hover {
    background: #f5f7fa;
  }
}

.date-number {
  font-size: 14px;
  margin-bottom: 4px;
}

.reservation-dots {
  display: flex;
  gap: 4px;
  justify-content: center;
  margin-bottom: 4px;

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;

    &.APPROVED {
      background: #67c23a;
    }

    &.PENDING {
      background: #e6a23c;
    }

    &.REJECTED {
      background: #f56c6c;
    }

    &.CANCELLED {
      background: #909399;
    }
  }
}

.reservation-count {
  font-size: 12px;
  color: #909399;
  text-align: center;
}
</style>
