<template>
  <div class="activity-management-page">
    <div class="page-header">
      <h2>活动管理</h2>
    </div>

    <el-card>
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索活动名称"
          style="width: 200px"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-select v-model="filterStatus" placeholder="活动状态" clearable style="width: 150px">
          <el-option label="筹备中" value="PLANNING" />
          <el-option label="待审批" value="PENDING_APPROVAL" />
          <el-option label="报名中" value="REGISTERING" />
          <el-option label="进行中" value="ONGOING" />
          <el-option label="已结束" value="COMPLETED" />
          <el-option label="已取消" value="CANCELLED" />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <el-table :data="activityList" v-loading="loading" style="width: 100%" stripe>
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="title" label="活动名称" min-width="200">
          <template #default="{ row }">
            <div class="activity-name">
              <el-avatar :size="40" :src="row.coverImageUrl" shape="square" />
              <div class="name-info">
                <div class="title">{{ row.title }}</div>
                <div class="type">{{ getActivityTypeLabel(row.activityType) }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="clubName" label="所属社团" width="150" />
        <el-table-column prop="startTime" label="开始时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.startTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="endTime" label="结束时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.endTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="participants" label="报名情况" width="120">
          <template #default="{ row }">
            {{ row.currentParticipants }}/{{ row.capacity || row.maxParticipants || '-' }}人
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button
              v-if="canEnd(row)"
              type="warning"
              link
              @click="handleEnd(row)"
            >
              结束
            </el-button>
            <el-button
              v-if="canCancel(row)"
              type="danger"
              link
              @click="handleCancel(row)"
            >
              取消
            </el-button>
            <el-button
              v-if="canDelete(row)"
              type="danger"
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 活动详情对话框 -->
    <el-dialog v-model="detailVisible" title="活动详情" width="600px">
      <el-descriptions :column="2" border v-if="currentActivity">
        <el-descriptions-item label="活动名称" :span="2">{{ currentActivity.title }}</el-descriptions-item>
        <el-descriptions-item label="所属社团">{{ currentActivity.clubName }}</el-descriptions-item>
        <el-descriptions-item label="活动类型">{{ getActivityTypeLabel(currentActivity.activityType) }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ formatDateTime(currentActivity.startTime) }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ formatDateTime(currentActivity.endTime) }}</el-descriptions-item>
        <el-descriptions-item label="活动地点">{{ currentActivity.location }}</el-descriptions-item>
        <el-descriptions-item label="人数限制">{{ currentActivity.capacity || currentActivity.maxParticipants }}人</el-descriptions-item>
        <el-descriptions-item label="当前报名">{{ currentActivity.currentParticipants }}人</el-descriptions-item>
        <el-descriptions-item label="活动状态">
          <el-tag :type="getStatusType(currentActivity.status)">
            {{ getStatusLabel(currentActivity.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="报名截止">{{ formatDateTime(currentActivity.registrationDeadline) || '无限制' }}</el-descriptions-item>
        <el-descriptions-item label="活动描述" :span="2">{{ currentActivity.description }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Search } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { formatDateTime, ActivityStatusMap, ActivityTypeMap } from '@campus/shared';
import type { Activity, PageResponse } from '@campus/shared';
import { apiClient } from '@campus/shared/api/client.axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const searchQuery = ref('');
const filterStatus = ref('');
const loading = ref(false);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const activityList = ref<Activity[]>([]);
const detailVisible = ref(false);
const currentActivity = ref<Activity | null>(null);

const STATUS_TYPE_MAP: Record<string, string> = {
  'PLANNING': 'info',
  'PENDING_APPROVAL': 'warning',
  'REGISTERING': 'success',
  'ONGOING': 'primary',
  'COMPLETED': 'info',
  'CANCELLED': 'danger',
};

function getStatusType(status: string) {
  return STATUS_TYPE_MAP[status] || 'info';
}

function getStatusLabel(status: string) {
  return ActivityStatusMap[status as keyof typeof ActivityStatusMap] || status;
}

function getActivityTypeLabel(type: string) {
  return ActivityTypeMap[type as keyof typeof ActivityTypeMap] || type;
}

function canEnd(activity: Activity) {
  // 任何非已结束/已取消状态的活动都可以结束
  return activity.status !== 'COMPLETED' && activity.status !== 'CANCELLED';
}

function canCancel(activity: Activity) {
  // 任何非已结束/已取消状态的活动都可以取消
  return activity.status !== 'COMPLETED' && activity.status !== 'CANCELLED';
}

function canDelete(activity: Activity) {
  // 已结束、已取消的活动可以删除
  return activity.status === 'COMPLETED' || activity.status === 'CANCELLED';
}

function handleSearch() {
  page.value = 1;
  loadData();
}

function handleReset() {
  searchQuery.value = '';
  filterStatus.value = '';
  page.value = 1;
  loadData();
}

function handleSizeChange(size: number) {
  pageSize.value = size;
  loadData();
}

function handlePageChange(current: number) {
  page.value = current;
  loadData();
}

function handleView(row: Activity) {
  currentActivity.value = row;
  detailVisible.value = true;
}

async function handleEnd(row: Activity) {
  try {
    await ElMessageBox.confirm(
      `确定要结束活动"${row.title}"吗？结束后活动将标记为已结束状态，不再允许报名。`,
      '确认结束活动',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    await apiClient.post(`/api/v1/admin/activities/${row.id}/end`);
    ElMessage.success('活动已结束');
    loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败');
    }
  }
}

async function handleCancel(row: Activity) {
  try {
    await ElMessageBox.confirm(
      `确定要取消活动"${row.title}"吗？取消后活动将标记为已取消状态。`,
      '确认取消活动',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'danger',
      }
    );

    await apiClient.post(`/api/v1/admin/activities/${row.id}/cancel`);
    ElMessage.success('活动已取消');
    loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败');
    }
  }
}

async function handleDelete(row: Activity) {
  try {
    await ElMessageBox.confirm(
      `确定要删除活动"${row.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'danger',
      }
    );

    await apiClient.delete(`/api/v1/admin/activities/${row.id}`);
    ElMessage.success('活动已删除');
    loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败');
    }
  }
}

async function loadData() {
  loading.value = true;
  try {
    const params: Record<string, any> = {
      page: page.value - 1,
      size: pageSize.value,
    };

    if (searchQuery.value) {
      params.keyword = searchQuery.value;
    }

    if (filterStatus.value) {
      params.status = filterStatus.value;
    }

    console.log('[Activity] Loading data with params:', params);
    const response = await apiClient.get<PageResponse<Activity>>('/api/v1/admin/activities', { params });
    console.log('[Activity] Response:', response);
    activityList.value = response.content || [];
    total.value = response.totalElements || 0;
    console.log('[Activity] Loaded', activityList.value.length, 'activities, total:', total.value);
  } catch (error: any) {
    console.error('[Activity] Load failed:', error);
    ElMessage.error(error.message || '获取活动列表失败');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<style scoped lang="scss">
.activity-management-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;

  h2 {
    margin: 0;
    color: #c9d1d9;
  }
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.activity-name {
  display: flex;
  align-items: center;
  gap: 12px;

  .name-info {
    .title {
      font-weight: 500;
      color: #c9d1d9;
    }

    .type {
      font-size: 12px;
      color: #8b949e;
      margin-top: 4px;
    }
  }
}

:deep(.el-card) {
  background: #161b22;
  border-color: #30363d;
  color: #c9d1d9;

  .el-card__body {
    background: #161b22;
  }
}

:deep(.el-table) {
  background: transparent;

  th, td {
    background: transparent;
    border-color: #30363d;
  }

  th {
    color: #c9d1d9;
  }

  td {
    color: #8b949e;
  }

  tr:hover > td {
    background: #0d1117;
  }
}

:deep(.el-descriptions) {
  .el-descriptions__label {
    background: #21262d;
    color: #c9d1d9;
  }

  .el-descriptions__content {
    background: #161b22;
    color: #c9d1d9;
  }
}
</style>
