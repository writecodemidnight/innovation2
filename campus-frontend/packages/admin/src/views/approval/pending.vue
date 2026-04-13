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
import { formatDateTime } from '@campus/shared';

const activeTab = ref('activity');
const loading = ref(false);
const pendingCount = ref(8);
const dialogVisible = ref(false);
const remark = ref('');
const currentItem = ref<any>({});

const activityApprovals = ref([
  {
    id: 1,
    title: '科技创新讲座',
    clubName: '科技创新社',
    applicant: '张三',
    applyTime: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 2,
    title: '编程工作坊',
    clubName: '计算机协会',
    applicant: '李四',
    applyTime: new Date(Date.now() - 7200000).toISOString(),
  },
]);

const resourceApprovals = ref([
  {
    id: 1,
    resourceName: '学生活动中心301报告厅',
    activityTitle: '科技创新讲座',
    startTime: new Date(Date.now() + 86400000).toISOString(),
    endTime: new Date(Date.now() + 86400000 + 7200000).toISOString(),
    applicant: '张三',
  },
]);

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
  try {
    // TODO: 调用审批API
    ElMessage.success('审批通过');
    dialogVisible.value = false;
    loadData();
  } catch {
    // 错误处理
  }
}

async function confirmReject() {
  try {
    // TODO: 调用审批API
    ElMessage.success('已拒绝');
    dialogVisible.value = false;
    loadData();
  } catch {
    // 错误处理
  }
}

async function loadData() {
  loading.value = true;
  try {
    // TODO: 调用API获取审批列表
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
