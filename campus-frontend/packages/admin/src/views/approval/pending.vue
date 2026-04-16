<template>
  <div class="approval-pending-page">
    <div class="page-header">
      <h2>待办审批</h2>
      <el-badge :value="pendingCount" class="pending-badge" />
    </div>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="活动审批" name="activity">
          <el-table :data="activityApprovals" v-loading="loading" style="width: 100%">
            <el-table-column prop="id" label="编号" width="80" />
            <el-table-column prop="title" label="活动名称" min-width="200" />
            <el-table-column prop="clubName" label="申请社团" width="150" />
            <el-table-column prop="applicant" label="申请人" width="120" />
            <el-table-column prop="applyTime" label="申请时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.applyTime) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleView(row)">查看</el-button>
                <el-button type="success" link @click="handleApprove(row)">通过</el-button>
                <el-button type="danger" link @click="handleReject(row)">拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="资源预约" name="resource">
          <el-table :data="resourceApprovals" v-loading="loading" style="width: 100%">
            <el-table-column prop="id" label="编号" width="80" />
            <el-table-column prop="resourceName" label="资源名称" min-width="200" />
            <el-table-column prop="activityTitle" label="关联活动" min-width="200" />
            <el-table-column label="预约时间" width="200">
              <template #default="{ row }">
                {{ formatDateTime(row.startTime) }}<br />
                至 {{ formatDateTime(row.endTime) }}
              </template>
            </el-table-column>
            <el-table-column prop="applicant" label="申请人" width="120" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleView(row)">查看</el-button>
                <el-button type="success" link @click="handleApprove(row)">通过</el-button>
                <el-button type="danger" link @click="handleReject(row)">拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 审批弹窗 -->
    <el-dialog v-model="dialogVisible" title="审批详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="类型">{{ currentItem.type }}</el-descriptions-item>
        <el-descriptions-item label="名称">{{ currentItem.name }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentItem.applicant }}</el-descriptions-item>
        <el-descriptions-item label="申请时间">{{ formatDateTime(currentItem.applyTime) }}</el-descriptions-item>
        <el-descriptions-item label="详情">{{ currentItem.detail }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-input
          v-model="remark"
          type="textarea"
          placeholder="请输入审批意见（可选）"
          :rows="3"
          style="margin-bottom: 16px"
        />
        <div class="dialog-actions">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmReject">拒绝</el-button>
          <el-button type="success" @click="confirmApprove">通过</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { formatDateTime, Endpoints } from '@campus/shared';
import { axiosClient } from '@campus/shared';
import { ElMessage } from 'element-plus';

const activeTab = ref('activity');
const loading = ref(false);
const pendingCount = ref(8);
const dialogVisible = ref(false);
const remark = ref('');
const currentItem = ref<any>({});

const activityApprovals = ref<any[]>([]);
const resourceApprovals = ref<any[]>([]);

// 审批类型映射
const approvalTypeMap: Record<string, string> = {
  activity: '活动审批',
  resource: '资源预约',
};

function handleTabChange() {
  loadData();
}

function handleView(row: any) {
  currentItem.value = {
    type: activeTab.value === 'activity' ? '活动审批' : '资源预约',
    name: row.title || row.resourceName,
    applicant: row.applicant,
    applyTime: row.applyTime,
    detail: JSON.stringify(row, null, 2),
  };
  dialogVisible.value = true;
}

function handleApprove(row: any) {
  currentItem.value = row;
  dialogVisible.value = true;
}

function handleReject(row: any) {
  currentItem.value = row;
  dialogVisible.value = true;
}

async function confirmApprove() {
  if (!currentItem.value?.id) return;
  try {
    await axiosClient.apiClient.post(Endpoints.approval.approve(currentItem.value.id), {
      remark: remark.value,
    });
    ElMessage.success('审批通过');
    dialogVisible.value = false;
    loadData();
  } catch (error: any) {
    ElMessage.error(error.message || '审批失败');
  }
}

async function confirmReject() {
  if (!currentItem.value?.id) return;
  try {
    await axiosClient.apiClient.post(Endpoints.approval.reject(currentItem.value.id), {
      remark: remark.value,
    });
    ElMessage.success('已拒绝');
    dialogVisible.value = false;
    loadData();
  } catch (error: any) {
    ElMessage.error(error.message || '审批失败');
  }
}

async function loadData() {
  loading.value = true;
  try {
    const data = await axiosClient.apiClient.get<any[]>(Endpoints.approval.pending, {
      params: { type: activeTab.value },
    });
    if (activeTab.value === 'activity') {
      activityApprovals.value = data || [];
    } else {
      resourceApprovals.value = data || [];
    }
    pendingCount.value = (activityApprovals.value.length + resourceApprovals.value.length);
  } catch (error: any) {
    ElMessage.error(error.message || '获取审批列表失败');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<style scoped lang="scss">
.approval-pending-page {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;

  h2 {
    margin: 0;
  }
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
