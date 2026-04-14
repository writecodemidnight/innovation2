<template>
  <div class="activity-detail-page">
    <div class="page-header">
      <h2>活动详情</h2>
      <div class="header-actions">
        <el-button @click="$router.back()">返回</el-button>
        <el-button type="primary" @click="handleEdit">编辑</el-button>
        <el-button type="success" @click="handleSubmit" v-if="activity?.status === ActivityStatus.PLANNING">
          提交审核
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-tag :type="getStatusType(activity?.status)">
                {{ getStatusLabel(activity?.status) }}
              </el-tag>
            </div>
          </template>

          <div v-if="activity" class="activity-info">
            <h3 class="activity-title">{{ activity.title }}</h3>
            <el-image
              v-if="activity.coverImageUrl"
              :src="activity.coverImageUrl"
              fit="cover"
              class="cover-image"
            />

            <el-descriptions :column="2" border>
              <el-descriptions-item label="活动类型">
                {{ getActivityTypeLabel(activity.activityType) }}
              </el-descriptions-item>
              <el-descriptions-item label="活动地点">
                {{ activity.location }}
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatDateTime(activity.startTime) }}
              </el-descriptions-item>
              <el-descriptions-item label="结束时间">
                {{ formatDateTime(activity.endTime) }}
              </el-descriptions-item>
              <el-descriptions-item label="报名人数">
                {{ activity.currentParticipants }}/{{ activity.maxParticipants }}
              </el-descriptions-item>
              <el-descriptions-item label="所属社团">
                {{ activity.clubName || '-' }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="description-section">
              <h4>活动描述</h4>
              <p class="description-content">{{ activity.description }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>参与者列表</span>
              <el-tag>{{ participants.length }}人报名</el-tag>
            </div>
          </template>

          <el-table :data="participants" v-loading="participantsLoading" size="small">
            <el-table-column prop="userName" label="姓名" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag size="small" :type="row.status === 'CHECKED_IN' ? 'success' : 'info'">
                  {{ row.status === 'CHECKED_IN' ? '已签到' : '已报名' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { formatDateTime, ActivityStatusMap, ActivityTypeMap, ActivityStatus } from '@campus/shared';
import { activityApi, type ActivityParticipantDto } from '@/api/activity';
import type { Activity } from '@campus/shared';
import { ElMessage, ElMessageBox } from 'element-plus';

const route = useRoute();
const router = useRouter();

const activity = ref<Activity | null>(null);
const participants = ref<ActivityParticipantDto[]>([]);
const loading = ref(false);
const participantsLoading = ref(false);

// 状态到Element UI标签类型的映射（提取到外部避免重复创建）
const STATUS_TYPE_MAP: Record<string, string> = {
  [ActivityStatus.PLANNING]: 'info',
  [ActivityStatus.PENDING_APPROVAL]: 'warning',
  [ActivityStatus.APPROVED]: 'success',
  [ActivityStatus.REGISTERING]: 'success',
  [ActivityStatus.ONGOING]: 'primary',
  [ActivityStatus.COMPLETED]: 'info',
  [ActivityStatus.REJECTED]: 'danger',
  [ActivityStatus.CANCELLED]: 'danger',
};

function getStatusType(status?: string) {
  return STATUS_TYPE_MAP[status || ''] || 'info';
}

function getStatusLabel(status?: string) {
  return ActivityStatusMap[status as keyof typeof ActivityStatusMap] || status || '-';
}

function getActivityTypeLabel(type?: string) {
  return ActivityTypeMap[type as keyof typeof ActivityTypeMap] || type || '-';
}

async function loadActivityDetail() {
  const id = Number(route.params.id);
  if (!id) return;

  loading.value = true;
  participantsLoading.value = true;
  try {
    // 并行加载活动详情和参与者列表
    const [activityRes, participantsRes] = await Promise.all([
      activityApi.getById(id),
      activityApi.getParticipants(id),
    ]);
    activity.value = activityRes;
    participants.value = participantsRes;
  } catch (error: any) {
    ElMessage.error(error.message || '获取活动详情失败');
  } finally {
    loading.value = false;
    participantsLoading.value = false;
  }
}

function handleEdit() {
  if (activity.value) {
    router.push(`/activities/${activity.value.id}/edit`);
  }
}

async function handleSubmit() {
  if (!activity.value) return;

  try {
    await ElMessageBox.confirm('确定要提交该活动进行审核吗？', '提示', {
      type: 'info',
    });
    await activityApi.submitForApproval(activity.value.id);
    ElMessage.success('提交成功，等待审核');
    loadActivityDetail();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '提交失败');
    }
  }
}

onMounted(() => {
  loadActivityDetail();
});
</script>

<style scoped lang="scss">
.activity-detail-page {
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

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-info {
  .activity-title {
    margin: 0 0 16px;
    font-size: 20px;
  }

  .cover-image {
    width: 100%;
    height: 200px;
    border-radius: 8px;
    margin-bottom: 16px;
  }

  .description-section {
    margin-top: 24px;

    h4 {
      margin: 0 0 12px;
      color: #303133;
    }

    .description-content {
      color: #606266;
      line-height: 1.6;
      white-space: pre-wrap;
    }
  }
}
</style>
