<template>
  <div class="activity-list-page">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索活动名称"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建活动
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-radio-group v-model="filterStatus" size="small" @change="handleFilter">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="REGISTERING">报名中</el-radio-button>
        <el-radio-button label="ONGOING">进行中</el-radio-button>
        <el-radio-button label="COMPLETED">已结束</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 活动列表 -->
    <el-table :data="activities" v-loading="loading" style="width: 100%">
      <el-table-column type="index" width="50" />
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
      <el-table-column prop="startTime" label="活动时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.startTime) }}
        </template>
      </el-table-column>
      <el-table-column prop="location" label="地点" width="150" />
      <el-table-column prop="participants" label="报名情况" width="120">
        <template #default="{ row }">
          <el-progress
            :percentage="Math.round((row.currentParticipants / row.maxParticipants) * 100)"
            :status="row.currentParticipants >= row.maxParticipants ? 'exception' : ''"
          />
          <div class="participant-text">
            {{ row.currentParticipants }}/{{ row.maxParticipants }}人
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="primary" link @click="handleView(row)">详情</el-button>
          <el-dropdown trigger="click">
            <el-button type="primary" link>
              更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleReport(row)">查看报告</el-dropdown-item>
                <el-dropdown-item divided @click="handleDelete(row)">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Search, Plus, ArrowDown } from '@element-plus/icons-vue';
import { formatDateTime, ActivityStatusMap, ActivityTypeMap } from '@campus/shared';
import type { Activity } from '@campus/shared';
import { activityApi } from '@/api/activity';
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();

// 搜索和筛选
const searchQuery = ref('');
const filterStatus = ref('');
const loading = ref(false);

// 分页
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 活动列表
const activities = ref<Partial<Activity>[]>([]);

// 加载数据
async function loadActivities() {
  loading.value = true;
  try {
    const params = {
      page: page.value - 1, // 后端分页从0开始
      size: pageSize.value,
      keyword: searchQuery.value || undefined,
      status: filterStatus.value || undefined,
    };
    const response = await activityApi.getList(params);
    activities.value = response.content;
    total.value = response.totalElements;
  } catch (error: any) {
    ElMessage.error(error.message || '获取活动列表失败');
  } finally {
    loading.value = false;
  }
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    PLANNING: 'info',
    PENDING_APPROVAL: 'warning',
    APPROVED: 'success',
    REGISTERING: 'success',
    ONGOING: 'primary',
    COMPLETED: 'info',
    REJECTED: 'danger',
    CANCELLED: 'danger',
  };
  return map[status] || 'info';
}

function getStatusLabel(status: string) {
  return ActivityStatusMap[status as any]?.label || status;
}

function getActivityTypeLabel(type: string) {
  return ActivityTypeMap[type as any] || type;
}

function handleSearch() {
  page.value = 1;
  loadActivities();
}

function handleFilter() {
  page.value = 1;
  loadActivities();
}

function handleCreate() {
  router.push('/activities/apply');
}

function handleEdit(row: Activity) {
  router.push(`/activities/edit/${row.id}`);
}

function handleView(row: Activity) {
  router.push(`/activities/${row.id}`);
}

function handleReport(row: Activity) {
  router.push(`/reports?activityId=${row.id}`);
}

async function handleDelete(row: Activity) {
  try {
    await ElMessageBox.confirm('确定要删除该活动吗？删除后不可恢复', '提示', {
      type: 'warning',
    });
    await activityApi.delete(row.id);
    ElMessage.success('删除成功');
    loadActivities();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败');
    }
  }
}

function handleSizeChange(val: number) {
  pageSize.value = val;
  loadActivities();
}

function handlePageChange(val: number) {
  page.value = val;
  loadActivities();
}

onMounted(() => {
  loadActivities();
});
</script>

<style scoped lang="scss">
.activity-list-page {
  padding: 20px;
}

.search-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;

  .el-input {
    flex: 1;
  }
}

.filter-bar {
  margin-bottom: 20px;
}

.activity-name {
  display: flex;
  align-items: center;
  gap: 12px;

  .name-info {
    .title {
      font-weight: 500;
      color: #303133;
    }

    .type {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
  }
}

.participant-text {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
