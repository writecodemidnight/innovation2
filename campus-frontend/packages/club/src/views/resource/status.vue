<template>
  <div class="resource-status-page">
    <div class="page-header">
      <h2>我的预约</h2>
    </div>

    <el-card>
      <el-table :data="resourceStore.reservations" v-loading="resourceStore.loading" style="width: 100%">
        <el-table-column prop="resourceName" label="资源名称" min-width="200" />
        <el-table-column prop="activityTitle" label="关联活动" min-width="200" />
        <el-table-column label="预约时间" width="200">
          <template #default="{ row }">
            {{ formatDateTime(row.startTime) }}<br />
            至 {{ formatDateTime(row.endTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="attendeesCount" label="使用人数" width="100" />
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

      <el-empty v-if="resourceStore.reservations.length === 0 && !resourceStore.loading" description="暂无预约记录" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { formatDateTime, ReservationStatusMap } from '@campus/shared';
import { useResourceStore } from '@/stores/resource';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { ResourceReservation } from '@campus/shared';

const resourceStore = useResourceStore();

function getStatusType(status: string) {
  return ReservationStatusMap[status as keyof typeof ReservationStatusMap]?.tag || 'info';
}

function getStatusLabel(status: string) {
  return ReservationStatusMap[status as keyof typeof ReservationStatusMap]?.label || status;
}

function handleView(row: ResourceReservation) {
  console.log('查看预约:', row);
}

async function handleCancel(row: ResourceReservation) {
  try {
    await ElMessageBox.confirm('确定要取消该预约吗？', '提示', { type: 'warning' });
    await resourceStore.cancelReservation(row.id);
    ElMessage.success('取消成功');
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '取消失败');
    }
  }
}

onMounted(() => {
  resourceStore.fetchMyReservations();
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
