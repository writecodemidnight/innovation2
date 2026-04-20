<template>
  <div class="fund-list-page">
    <div class="page-header">
      <h2>资金申请管理</h2>
      <el-button type="primary" @click="$router.push('/funds/apply')">
        申请资金
      </el-button>
    </div>

    <el-card v-loading="loading">
      <el-table :data="applications" style="width: 100%">
        <el-table-column prop="id" label="申请编号" width="100" />
        <el-table-column prop="amount" label="申请金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="purpose" label="用途" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="申请时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row.id)">
              详情
            </el-button>
            <el-button
              v-if="row.status === 'PENDING'"
              type="danger"
              link
              @click="handleCancel(row.id)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="size"
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
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { formatDateTime } from '@campus/shared';
import type { FundApplication } from '@campus/shared';
import { fundApi } from '@/api/fund';

const router = useRouter();
const loading = ref(false);
const applications = ref<FundApplication[]>([]);
const page = ref(1);
const size = ref(10);
const total = ref(0);

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    PENDING: 'warning',
    APPROVED: 'success',
    REJECTED: 'danger',
    CANCELLED: 'info',
  };
  return map[status] || 'info';
};

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    PENDING: '待审批',
    APPROVED: '已通过',
    REJECTED: '已拒绝',
    CANCELLED: '已取消',
  };
  return map[status] || status;
};

const loadApplications = async () => {
  loading.value = true;
  try {
    const response = await fundApi.getMyApplications(page.value - 1, size.value);
    applications.value = response.content || [];
    total.value = response.totalElements || 0;
  } catch (error: any) {
    ElMessage.error(error.message || '获取申请列表失败');
  } finally {
    loading.value = false;
  }
};

const viewDetail = (id: number) => {
  router.push(`/funds/${id}`);
};

const handleCancel = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要取消该资金申请吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });

    await fundApi.cancel(id);
    ElMessage.success('取消成功');
    loadApplications();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '取消失败');
    }
  }
};

const handleSizeChange = (newSize: number) => {
  size.value = newSize;
  page.value = 1;
  loadApplications();
};

const handlePageChange = (newPage: number) => {
  page.value = newPage;
  loadApplications();
};

onMounted(() => {
  loadApplications();
});
</script>

<style scoped lang="scss">
.fund-list-page {
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

.amount {
  color: #f56c6c;
  font-weight: 600;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
