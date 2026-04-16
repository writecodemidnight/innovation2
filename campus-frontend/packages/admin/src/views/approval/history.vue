<template>
  <div class="approval-history-page">
    <div class="page-header">
      <h2>审批历史</h2>
    </div>

    <el-card>
      <div class="filter-bar">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />
        <el-select v-model="filterStatus" placeholder="审批结果" clearable>
          <el-option label="通过" value="approved" />
          <el-option label="拒绝" value="rejected" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>

      <el-table :data="historyList" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'activity' ? 'primary' : 'success'">
              {{ row.type === 'activity' ? '活动' : '资源' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="applicant" label="申请人" width="120" />
        <el-table-column prop="approver" label="审批人" width="120" />
        <el-table-column prop="approveTime" label="审批时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.approveTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="result" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="row.result === 'approved' ? 'success' : 'danger'">
              {{ row.result === 'approved' ? '通过' : '拒绝' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="审批意见" min-width="200" show-overflow-tooltip />
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { formatDateTime, Endpoints } from '@campus/shared';
import { axiosClient } from '@campus/shared';
import { ElMessage } from 'element-plus';

const dateRange = ref<string[]>([]);
const filterStatus = ref('');
const loading = ref(false);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);

const historyList = ref<any[]>([]);

function handleSearch() {
  page.value = 1;
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

    const response = await axiosClient.apiClient.get<any>(Endpoints.approval.history, { params });
    historyList.value = response?.content || [];
    total.value = response?.totalElements || 0;
  } catch (error: any) {
    ElMessage.error(error.message || '获取审批历史失败');
  } finally {
    loading.value = false;
  }
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
  }
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
