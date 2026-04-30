<template>
  <div class="approval-history-page">
    <div class="page-header">
      <h2>审批历史</h2>
    </div>

    <el-card>
      <div class="filter-bar">
        <el-select v-model="historyType" placeholder="审批类型" style="width: 150px">
          <el-option label="活动审批" value="activities" />
          <el-option label="资金审批" value="fundApplications" />
          <el-option label="资源预约" value="resourceBookings" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="审批结果" clearable style="width: 150px">
          <el-option label="通过" value="APPROVED" />
          <el-option label="拒绝" value="REJECTED" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <el-table :data="historyList" v-loading="loading" style="width: 100%" stripe>
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" size="small">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="200">
          <template #default="{ row }">
            <el-tooltip :content="row.detail" placement="top" :show-after="500">
              <span class="ellipsis">{{ row.name }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="applicantName" label="申请人" width="120" />
        <el-table-column prop="reviewerName" label="审批人" width="120" />
        <el-table-column prop="reviewedAt" label="审批时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.reviewedAt) }}
          </template>
        </el-table-column>
        <el-table-column prop="result" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="row.result === 'APPROVED' ? 'success' : 'danger'" size="small">
              {{ row.result === 'APPROVED' ? '通过' : '拒绝' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="comment" label="审批意见" min-width="200" show-overflow-tooltip />
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Search } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { Endpoints } from '@campus/shared';
import type { PageResponse } from '@campus/shared';
import { apiClient } from '@campus/shared/api/client.axios';

const historyType = ref('activities');
const filterStatus = ref('');
const dateRange = ref<string[]>([]);
const loading = ref(false);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);

const historyList = ref<any[]>([]);

function getTypeTagType(type: string) {
  const map: Record<string, string> = {
    activity: 'primary',
    fund: 'warning',
    resource: 'success',
  };
  return map[type] || 'info';
}

function getTypeLabel(type: string) {
  const map: Record<string, string> = {
    activity: '活动',
    fund: '资金',
    resource: '资源',
  };
  return map[type] || type;
}

function handleSearch() {
  page.value = 1;
  loadData();
}

function handleReset() {
  historyType.value = 'activities';
  filterStatus.value = '';
  dateRange.value = [];
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

async function loadData() {
  loading.value = true;
  try {
    const params: Record<string, any> = {
      page: page.value - 1,
      size: pageSize.value,
    };

    if (dateRange.value?.length === 2) {
      params.startDate = dateRange.value[0];
      params.endDate = dateRange.value[1];
    }

    if (filterStatus.value) {
      params.status = filterStatus.value;
    }

    // 根据类型选择不同的端点
    let endpoint = '';
    switch (historyType.value) {
      case 'activities':
        endpoint = Endpoints.adminHistory.activities;
        break;
      case 'fundApplications':
        endpoint = Endpoints.adminHistory.fundApplications;
        break;
      case 'resourceBookings':
        endpoint = Endpoints.adminHistory.resourceBookings;
        break;
      default:
        endpoint = Endpoints.adminHistory.activities;
    }

    const response = await apiClient.get<{ data: PageResponse<any> }>(endpoint, { params });
    historyList.value = (response.data.content || []).map((item: any) => ({
      ...item,
      type: historyType.value === 'activities' ? 'activity' :
            historyType.value === 'fundApplications' ? 'fund' : 'resource',
    }));
    total.value = response.data.totalElements || 0;
  } catch (error: any) {
    ElMessage.error(error.message || '获取审批历史失败');
  } finally {
    loading.value = false;
  }
}

function formatDateTime(date: string | undefined) {
  if (!date) return '-';
  const d = new Date(date);
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

onMounted(() => {
  loadData();
});
</script>

<style scoped lang="scss">
.approval-history-page {
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

.ellipsis {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
</style>
