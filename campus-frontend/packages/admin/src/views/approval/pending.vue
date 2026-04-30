<template>
  <div class="approval-pending-page">
    <div class="page-header">
      <h2>待办审批</h2>
      <el-badge :value="approvalStore.totalPending" class="pending-badge" type="danger" />
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="8">
        <el-card class="stat-card" @click="switchTab('activity')" :class="{ active: activeTab === 'activity' }">
          <div class="stat-icon" style="background: rgba(0, 212, 170, 0.1)">
            <el-icon size="32" color="#00d4aa"><Calendar /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #00d4aa">{{ approvalStore.approvalCounts?.activities || 0 }}</div>
            <div class="stat-label">活动待审批</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card class="stat-card" @click="switchTab('fund')" :class="{ active: activeTab === 'fund' }">
          <div class="stat-icon" style="background: rgba(163, 113, 247, 0.1)">
            <el-icon size="32" color="#a371f7"><Money /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #a371f7">{{ approvalStore.approvalCounts?.fundApplications || 0 }}</div>
            <div class="stat-label">资金待审批</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card class="stat-card" @click="switchTab('resource')" :class="{ active: activeTab === 'resource' }">
          <div class="stat-icon" style="background: rgba(88, 166, 255, 0.1)">
            <el-icon size="32" color="#58a6ff"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #58a6ff">{{ approvalStore.approvalCounts?.resourceBookings || 0 }}</div>
            <div class="stat-label">资源待审批</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 活动审批 -->
        <el-tab-pane label="活动审批" name="activity">
          <el-table :data="approvalStore.pendingActivities" v-loading="approvalStore.loading" style="width: 100%">
            <el-table-column prop="id" label="编号" width="80" />
            <el-table-column prop="title" label="活动名称" min-width="180" />
            <el-table-column prop="clubName" label="申请社团" width="140">
              <template #default="{ row }">
                {{ row.clubName || '社团' + row.clubId }}
              </template>
            </el-table-column>
            <el-table-column prop="location" label="活动地点" min-width="150" />
            <el-table-column label="活动时间" width="200">
              <template #default="{ row }">
                <div>{{ formatDateTime(row.startTime) }}</div>
                <div style="color: #6e7681; font-size: 12px">至 {{ formatDateTime(row.endTime) }}</div>
              </template>
            </el-table-column>
            <el-table-column label="人数上限" width="100">
              <template #default="{ row }">
                {{ row.capacity || row.maxParticipants || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleView(row, 'activity')">查看</el-button>
                <el-button type="success" link size="small" @click="handleApprove(row, 'activity')">通过</el-button>
                <el-button type="danger" link size="small" @click="handleReject(row, 'activity')">拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!approvalStore.loading && approvalStore.pendingActivities.length === 0" description="暂无待审批活动" />
        </el-tab-pane>

        <!-- 资金审批 -->
        <el-tab-pane label="资金审批" name="fund">
          <el-table :data="approvalStore.pendingFundApplications" v-loading="approvalStore.loading" style="width: 100%">
            <el-table-column prop="id" label="编号" width="80" />
            <el-table-column label="关联活动" min-width="180">
              <template #default="{ row }">
                {{ row.activityTitle || '活动' + row.activityId }}
              </template>
            </el-table-column>
            <el-table-column label="申请社团" width="140">
              <template #default="{ row }">
                {{ row.clubName || '社团' + row.clubId }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="申请金额" width="120">
              <template #default="{ row }">
                <span style="color: #f0883e; font-weight: 600">¥{{ row.amount?.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="purpose" label="用途说明" min-width="200" show-overflow-tooltip />
            <el-table-column label="申请人" width="120">
              <template #default="{ row }">
                {{ row.applicantName || '用户' + row.applicantId }}
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="申请时间" width="160">
              <template #default="{ row }">
                {{ formatDateTime(row.createdAt) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleView(row, 'fund')">查看</el-button>
                <el-button type="success" link size="small" @click="handleApprove(row, 'fund')">通过</el-button>
                <el-button type="danger" link size="small" @click="handleReject(row, 'fund')">拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!approvalStore.loading && approvalStore.pendingFundApplications.length === 0" description="暂无待审批资金申请" />
        </el-tab-pane>

        <!-- 资源预约审批 -->
        <el-tab-pane label="资源预约" name="resource">
          <el-table :data="approvalStore.pendingResourceBookings" v-loading="approvalStore.loading" style="width: 100%">
            <el-table-column prop="id" label="编号" width="80" />
            <el-table-column label="资源名称" min-width="150">
              <template #default="{ row }">
                {{ row.resourceName || '资源' + row.resourceId }}
              </template>
            </el-table-column>
            <el-table-column prop="resourceType" label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.resourceType || '设备' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="关联活动" min-width="150">
              <template #default="{ row }">
                {{ row.activityTitle || '活动' + row.activityId }}
              </template>
            </el-table-column>
            <el-table-column label="预约时间" width="200">
              <template #default="{ row }">
                <div>{{ formatDateTime(row.startTime) }}</div>
                <div style="color: #6e7681; font-size: 12px">至 {{ formatDateTime(row.endTime) }}</div>
              </template>
            </el-table-column>
            <el-table-column label="申请人" width="120">
              <template #default="{ row }">
                {{ row.applicantName || '用户' + row.applicantId }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'PENDING' ? 'warning' : 'success'">{{ row.status === 'PENDING' ? '待审批' : row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleView(row, 'resource')">查看</el-button>
                <el-button type="success" link size="small" @click="handleApprove(row, 'resource')">通过</el-button>
                <el-button type="danger" link size="small" @click="handleReject(row, 'resource')">拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!approvalStore.loading && approvalStore.pendingResourceBookings.length === 0" description="暂无待审批资源预约" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 审批弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-descriptions :column="1" border v-if="currentItem">
        <template v-if="currentType === 'activity'">
          <el-descriptions-item label="活动名称">{{ (currentItem as Activity).title }}</el-descriptions-item>
          <el-descriptions-item label="申请社团">{{ (currentItem as Activity).clubName || '社团' + (currentItem as Activity).clubId }}</el-descriptions-item>
          <el-descriptions-item label="活动地点">{{ (currentItem as Activity).location }}</el-descriptions-item>
          <el-descriptions-item label="活动时间">{{ formatDateTime((currentItem as Activity).startTime) }} 至 {{ formatDateTime((currentItem as Activity).endTime) }}</el-descriptions-item>
          <el-descriptions-item label="人数上限">{{ (currentItem as Activity).capacity || (currentItem as Activity).maxParticipants || '-' }}人</el-descriptions-item>
          <el-descriptions-item label="活动描述">{{ (currentItem as Activity).description }}</el-descriptions-item>
        </template>
        <template v-if="currentType === 'fund'">
          <el-descriptions-item label="关联活动">{{ (currentItem as FundApplication).activityTitle || '活动' + (currentItem as FundApplication).activityId }}</el-descriptions-item>
          <el-descriptions-item label="申请社团">{{ (currentItem as FundApplication).clubName || '社团' + (currentItem as FundApplication).clubId }}</el-descriptions-item>
          <el-descriptions-item label="申请金额">¥{{ (currentItem as FundApplication).amount?.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="用途说明">{{ (currentItem as FundApplication).purpose }}</el-descriptions-item>
          <el-descriptions-item label="预算明细">{{ (currentItem as FundApplication).budgetBreakdown || '无' }}</el-descriptions-item>
          <el-descriptions-item label="申请人">{{ (currentItem as FundApplication).applicantName || '用户' + (currentItem as FundApplication).applicantId }}</el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ formatDateTime((currentItem as FundApplication).createdAt) }}</el-descriptions-item>
        </template>
        <template v-if="currentType === 'resource'">
          <el-descriptions-item label="资源名称">{{ (currentItem as ResourceBooking).resourceName || '资源' + (currentItem as ResourceBooking).resourceId }}</el-descriptions-item>
          <el-descriptions-item label="资源类型">{{ (currentItem as ResourceBooking).resourceType || '设备' }}</el-descriptions-item>
          <el-descriptions-item label="关联活动">{{ (currentItem as ResourceBooking).activityTitle || '活动' + (currentItem as ResourceBooking).activityId }}</el-descriptions-item>
          <el-descriptions-item label="预约时间">{{ formatDateTime((currentItem as ResourceBooking).startTime) }} 至 {{ formatDateTime((currentItem as ResourceBooking).endTime) }}</el-descriptions-item>
          <el-descriptions-item label="申请人">{{ (currentItem as ResourceBooking).applicantName || '用户' + (currentItem as ResourceBooking).applicantId }}</el-descriptions-item>
        </template>
      </el-descriptions>
      <el-input
        v-model="comment"
        type="textarea"
        placeholder="请输入审批意见（可选）"
        :rows="3"
        style="margin-top: 16px"
      />
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject" v-if="actionType === 'reject' || actionType === 'view'">拒绝</el-button>
        <el-button type="success" @click="confirmApprove" v-if="actionType === 'approve' || actionType === 'view'">通过</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { Calendar, Money, OfficeBuilding } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { useApprovalStore } from '@/stores';
import type { Activity, ResourceBooking, FundApplication } from '@campus/shared';

type ApprovalType = 'activity' | 'fund' | 'resource';
type ActionType = 'view' | 'approve' | 'reject';

const approvalStore = useApprovalStore();
const activeTab = ref<ApprovalType>('activity');
const dialogVisible = ref(false);
const comment = ref('');
const currentItem = ref<Activity | ResourceBooking | FundApplication | null>(null);
const currentType = ref<ApprovalType>('activity');
const actionType = ref<ActionType>('view');

const dialogTitle = computed(() => {
  const titles: Record<ApprovalType, string> = {
    activity: '活动审批详情',
    fund: '资金申请审批详情',
    resource: '资源预约审批详情',
  };
  return titles[currentType.value] || '审批详情';
});

function getStatusType(status: string) {
  const map: Record<string, string> = {
    PENDING: 'warning',
    APPROVED: 'success',
    REJECTED: 'danger',
    CANCELLED: 'info',
  };
  return map[status] || 'info';
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    PENDING: '待审批',
    APPROVED: '已通过',
    REJECTED: '已拒绝',
    CANCELLED: '已取消',
  };
  return map[status] || status;
}

function handleTabChange(tab: ApprovalType) {
  loadTabData(tab);
}

function handleView(item: Activity | ResourceBooking | FundApplication, type: ApprovalType) {
  currentItem.value = item;
  currentType.value = type;
  actionType.value = 'view';
  comment.value = '';
  dialogVisible.value = true;
}

function handleApprove(item: Activity | ResourceBooking | FundApplication, type: ApprovalType) {
  currentItem.value = item;
  currentType.value = type;
  actionType.value = 'approve';
  comment.value = '';
  dialogVisible.value = true;
}

function handleReject(item: Activity | ResourceBooking | FundApplication, type: ApprovalType) {
  currentItem.value = item;
  currentType.value = type;
  actionType.value = 'reject';
  comment.value = '';
  dialogVisible.value = true;
}

async function confirmApprove() {
  if (!currentItem.value?.id) return;
  try {
    switch (currentType.value) {
      case 'activity':
        await approvalStore.approveActivity(currentItem.value.id, comment.value);
        break;
      case 'fund':
        await approvalStore.approveFundApplication(currentItem.value.id, comment.value);
        break;
      case 'resource':
        await approvalStore.approveResourceBooking(currentItem.value.id, comment.value);
        break;
    }
    ElMessage.success('审批通过');
    dialogVisible.value = false;
    comment.value = '';
  } catch (error: any) {
    ElMessage.error(error.message || '审批失败');
  }
}

async function confirmReject() {
  if (!currentItem.value?.id) return;
  try {
    switch (currentType.value) {
      case 'activity':
        await approvalStore.rejectActivity(currentItem.value.id, comment.value);
        break;
      case 'fund':
        await approvalStore.rejectFundApplication(currentItem.value.id, comment.value);
        break;
      case 'resource':
        await approvalStore.rejectResourceBooking(currentItem.value.id, comment.value);
        break;
    }
    ElMessage.success('已拒绝');
    dialogVisible.value = false;
    comment.value = '';
  } catch (error: any) {
    ElMessage.error(error.message || '审批失败');
  }
}

async function loadTabData(tab: ApprovalType) {
  switch (tab) {
    case 'activity':
      await approvalStore.fetchPendingActivities();
      break;
    case 'fund':
      await approvalStore.fetchPendingFundApplications();
      break;
    case 'resource':
      await approvalStore.fetchPendingResourceBookings();
      break;
  }
}

function switchTab(tab: ApprovalType) {
  activeTab.value = tab;
  loadTabData(tab);
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

onMounted(async () => {
  await approvalStore.fetchApprovalCounts();
  await loadTabData(activeTab.value);
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
    color: #c9d1d9;
  }
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover, &.active {
    border-color: #58a6ff;
    transform: translateY(-2px);
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.2;
  }

  .stat-label {
    font-size: 14px;
    color: #8b949e;
    margin-top: 4px;
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

:deep(.el-tabs__item) {
  color: #8b949e;

  &.is-active {
    color: #58a6ff;
  }
}

:deep(.el-descriptions__label) {
  background: #0d1117;
  color: #8b949e;
}

:deep(.el-descriptions__content) {
  background: #161b22;
  color: #c9d1d9;
}
</style>
