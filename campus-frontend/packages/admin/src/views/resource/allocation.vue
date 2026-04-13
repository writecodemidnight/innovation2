<template>
  <div class="resource-allocation-page">
    <div class="page-header">
      <h2>资源分配</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>资源占用日历</span>
          </template>
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
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>{{ selectedDate }} 预约情况</span>
          </template>
          <el-timeline v-if="selectedDateReservations.length > 0">
            <el-timeline-item
              v-for="res in selectedDateReservations"
              :key="res.id"
              :type="getTimelineType(res.status)"
              :timestamp="formatTimeRange(res.startTime, res.endTime)"
            >
              <h4>{{ res.resourceName }}</h4>
              <p>活动：{{ res.activityTitle }}</p>
              <p>社团：{{ res.clubName }}</p>
              <el-tag :type="getStatusType(res.status)" size="small">
                {{ getStatusLabel(res.status) }}
              </el-tag>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="当日无预约" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const currentDate = ref(new Date());
const selectedDate = ref(new Date().toISOString().split('T')[0]);
const selectedDateReservations = ref<any[]>([]);

const reservations = ref([
  {
    id: 1,
    resourceName: '301报告厅',
    activityTitle: '科技创新讲座',
    clubName: '科技创新社',
    startTime: '2024-03-15T14:00:00',
    endTime: '2024-03-15T16:00:00',
    status: 'APPROVED',
  },
]);

function getReservationsByDate(dateStr: string) {
  return reservations.value.filter(r => r.startTime.startsWith(dateStr));
}

function handleDateClick(dateStr: string) {
  selectedDate.value = dateStr;
  selectedDateReservations.value = getReservationsByDate(dateStr);
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
.resource-allocation-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;

  h2 {
    margin: 0;
  }
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
