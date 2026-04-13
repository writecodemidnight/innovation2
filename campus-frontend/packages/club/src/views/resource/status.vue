<template>
  <div class="resource-status-page">
    <div class="page-header">
      <h2>我的预约</h2>
    </div>

    <el-card>
      <el-table :data="reservations" v-loading="loading" style="width: 100%">
        <el-table-column prop="resourceName" label="资源名称" min-width="200" />
        <el-table-column prop="activityTitle" label="关联活动" min-width="200" />
        <el-table-column label="预约时间" width="200">
          <template #default="{ row }">
            {{ formatDateTime(row.startTime) }}<br />
            至 {{ formatDateTime(row.endTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="attendees" label="使用人数" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button
              v-if="row.status === 'PENDING'"
              type="danger"
              link
              @click="handleCancel(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { formatDateTime } from '@campus/shared';

const loading = ref(false);
const reservations = ref([
  {
    id: 1,
    resourceId: 1,
    resourceName: '学生活动中心301报告厅',
    activityTitle: '科技创新讲座',
    startTime: new Date(Date.now() + 86400000).toISOString(),
    endTime: new Date(Date.now() + 86400000 + 7200000).toISOString(),
    attendees: 80,
    status: 'APPROVED',
  },
  {
    id: 2,
    resourceId: 2,
    resourceName: '学生活动中心302会议室',
    activityTitle: '编程工作坊',
    startTime: new Date(Date.now() + 172800000).toISOString(),
    endTime: new Date(Date.now() + 172800000 + 10800000).toISOString(),
    attendees: 30,
    status: 'PENDING',
  },
]);

function getStatusType(status: string) {
  const map: Record<string, string> = {
    APPROVED: 'success',
    PENDING: 'warning',
    REJECTED: 'danger',
    CANCELLED: 'info',
  };
  return map[status] || 'info';
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    APPROVED: '已通过',
    PENDING: '审核中',
    REJECTED: '已拒绝',
    CANCELLED: '已取消',
  };
  return map[status] || status;
}

function handleView(row: any) {
  console.log('查看预约:', row);
}

async function handleCancel(row: any) {
  try {
    await ElMessageBox.confirm('确定要取消该预约吗？', '提示', { type: 'warning' });
    // TODO: 调用取消API
    ElMessage.success('取消成功');
    loadReservations();
  } catch {
    // 取消操作
  }
}

async function loadReservations() {
  loading.value = true;
  try {
    // TODO: 调用API获取预约列表
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadReservations();
});
</script>

<style scoped lang="scss">
.resource-status-page {
  padding: 20px;

  .page-header {
    margin-bottom: 24px;

    h2 {
      margin: 0;
    }
  }
}
</style>
