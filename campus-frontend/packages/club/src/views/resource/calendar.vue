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
      <el-select v-model="selectedResource" placeholder="选择资源" clearable style="width: 200px">
        <el-option
          v-for="resource in resources"
          :key="resource.id"
          :label="resource.name"
          :value="resource.id"
        />
      </el-select>
    </div>

    <!-- 日历视图 -->
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
        </div>
      </template>
    </el-calendar>

    <!-- 预约详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="预约详情" width="600px">
      <el-timeline>
        <el-timeline-item
          v-for="res in selectedDateReservations"
          :key="res.id"
          :type="getTimelineType(res.status)"
          :timestamp="formatTimeRange(res.startTime, res.endTime)"
        >
          <h4>{{ res.resourceName }}</h4>
          <p>活动：{{ res.activityTitle }}</p>
          <p>状态：<el-tag :type="getStatusType(res.status)">{{ getStatusLabel(res.status) }}</el-tag></p>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { Plus } from '@element-plus/icons-vue';

const router = useRouter();
const currentDate = ref(new Date());
const selectedResource = ref('');
const dialogVisible = ref(false);
const selectedDateReservations = ref<any[]>([]);

// 资源列表
const resources = ref([
  { id: 1, name: '学生活动中心301报告厅' },
  { id: 2, name: '学生活动中心302会议室' },
  { id: 3, name: '室外篮球场' },
  { id: 4, name: '礼堂' },
]);

// 预约数据
const reservations = ref([
  {
    id: 1,
    resourceId: 1,
    resourceName: '学生活动中心301报告厅',
    activityTitle: '科技创新讲座',
    startTime: '2024-03-15T14:00:00',
    endTime: '2024-03-15T16:00:00',
    status: 'APPROVED',
  },
  {
    id: 2,
    resourceId: 2,
    resourceName: '学生活动中心302会议室',
    activityTitle: '社团例会',
    startTime: '2024-03-15T18:00:00',
    endTime: '2024-03-15T20:00:00',
    status: 'PENDING',
  },
]);

function getReservationsByDate(dateStr: string) {
  return reservations.value.filter(r => r.startTime.startsWith(dateStr));
}

function handleDateClick(dateStr: string) {
  selectedDateReservations.value = getReservationsByDate(dateStr);
  if (selectedDateReservations.value.length > 0) {
    dialogVisible.value = true;
  }
}

function handleApply() {
  router.push('/resources/apply');
}

function formatTimeRange(start: string, end: string) {
  const s = new Date(start).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  const e = new Date(end).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  return `${s} - ${e}`;
}

function getTimelineType(status: string) {
  const map: Record<string, any> = {
    APPROVED: 'primary',
    PENDING: 'warning',
    REJECTED: 'danger',
  };
  return map[status] || 'info';
}

function getStatusType(status: string) {
  const map: Record<string, any> = {
    APPROVED: 'success',
    PENDING: 'warning',
    REJECTED: 'danger',
  };
  return map[status] || 'info';
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    APPROVED: '已通过',
    PENDING: '审核中',
    REJECTED: '已拒绝',
  };
  return map[status] || status;
}
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
}

.calendar-cell {
  height: 100%;
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
  }
}
</style>
