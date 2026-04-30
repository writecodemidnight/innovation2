<template>
  <div class="activity-apply-page">
    <div class="page-header">
      <h2>{{ isEdit ? '编辑活动' : '新建活动' }}</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      class="activity-form"
    >
      <!-- 基本信息 -->
      <el-card class="form-section">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>

        <el-form-item label="活动标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入活动标题" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="活动类型" prop="activityType">
          <el-select v-model="form.activityType" placeholder="请选择活动类型">
            <el-option
              v-for="(label, value) in ActivityTypeMap"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="活动时间" prop="timeRange">
          <el-date-picker
            v-model="form.timeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>

        <el-form-item label="活动地点" prop="location">
          <el-input v-model="form.location" placeholder="请输入活动地点" />
        </el-form-item>

        <el-form-item label="活动封面" prop="coverImageUrl">
          <el-upload
            class="cover-uploader"
            action="/api/upload"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
          >
            <img v-if="form.coverImageUrl" :src="form.coverImageUrl" class="cover-image" />
            <el-icon v-else class="cover-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-card>

      <!-- 参与设置 -->
      <el-card class="form-section">
        <template #header>
          <div class="card-header">
            <span>参与设置</span>
          </div>
        </template>

        <el-form-item label="人数限制" prop="maxParticipants">
          <el-input-number v-model="form.maxParticipants" :min="1" :max="1000" />
          <span class="form-tip">人（1-1000）</span>
        </el-form-item>

        <el-form-item label="报名截止时间" prop="registrationDeadline">
          <el-date-picker
            v-model="form.registrationDeadline"
            type="datetime"
            placeholder="选择报名截止时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
      </el-card>

      <!-- 活动详情 -->
      <el-card class="form-section">
        <template #header>
          <div class="card-header">
            <span>活动详情</span>
          </div>
        </template>

        <el-form-item label="活动描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="6"
            placeholder="请输入活动描述，包括活动流程、注意事项等"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-card>

      <!-- 提交按钮 -->
      <div class="form-actions">
        <el-button @click="$router.back()">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          提交审核
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Plus } from '@element-plus/icons-vue';
import { ActivityType, ActivityTypeMap } from '@campus/shared';
import type { ActivityCreateRequest } from '@campus/shared';
import type { FormInstance, FormRules, UploadProps } from 'element-plus';
import { activityApi } from '@/api/activity';
import { useUserStore } from '@/stores/user';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const formRef = ref<FormInstance>();
const submitting = ref(false);
const isEdit = ref(false);
const activityId = ref<number | null>(null);

// 上传请求头
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`
};

// 表单数据
const form = reactive({
  title: '',
  activityType: '',
  timeRange: [] as string[],
  location: '',
  coverImageUrl: '',
  maxParticipants: 50,
  registrationDeadline: '',
  description: '',
});

// 表单验证规则
const rules: FormRules = {
  title: [
    { required: true, message: '请输入活动标题', trigger: 'blur' },
    { min: 5, max: 100, message: '标题长度应为5-100个字符', trigger: 'blur' }
  ],
  activityType: [{ required: true, message: '请选择活动类型', trigger: 'change' }],
  timeRange: [
    { required: true, message: '请选择活动时间', trigger: 'change' },
    {
      validator: (rule: any, value: string[], callback: Function) => {
        if (value && value.length === 2) {
          const startTime = new Date(value[0]);
          const endTime = new Date(value[1]);
          const now = new Date();

          if (startTime >= endTime) {
            callback(new Error('开始时间必须早于结束时间'));
          } else if (startTime < now) {
            callback(new Error('开始时间不能早于当前时间'));
          } else {
            callback();
          }
        } else {
          callback(new Error('请选择完整的活动时间'));
        }
      },
      trigger: 'change'
    }
  ],
  location: [
    { required: true, message: '请输入活动地点', trigger: 'blur' },
    { min: 3, max: 100, message: '地点长度应为3-100个字符', trigger: 'blur' }
  ],
  maxParticipants: [
    { required: true, message: '请设置人数限制', trigger: 'blur' },
    { type: 'number', min: 1, max: 1000, message: '人数应在1-1000之间', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入活动描述', trigger: 'blur' },
    { min: 20, max: 2000, message: '描述长度应为20-2000个字符', trigger: 'blur' }
  ],
};

// 上传相关
const handleUploadSuccess: UploadProps['onSuccess'] = (response) => {
  console.log('Upload response:', response);
  if ((response.code === 'SUCCESS' || response.success) && response.data) {
    form.coverImageUrl = response.data;
    ElMessage.success('上传成功');
  } else {
    ElMessage.error(response.message || '上传失败');
  }
};

const beforeUpload: UploadProps['beforeUpload'] = (rawFile) => {
  const isJpgOrPng = rawFile.type === 'image/jpeg' || rawFile.type === 'image/png';
  if (!isJpgOrPng) {
    ElMessage.error('只支持 JPG/PNG 格式!');
  }
  const isLt2M = rawFile.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!');
  }
  return isJpgOrPng && isLt2M;
};

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        const data: ActivityCreateRequest = {
          title: form.title,
          description: form.description,
          clubId: userStore.userInfo?.clubId,
          activityType: form.activityType as ActivityType,
          startTime: form.timeRange[0],
          endTime: form.timeRange[1],
          location: form.location,
          capacity: form.maxParticipants,
          coverImageUrl: form.coverImageUrl,
          registrationDeadline: form.registrationDeadline,
        };

        if (isEdit.value && activityId.value) {
          await activityApi.update(activityId.value, data);
          ElMessage.success('更新成功');
        } else {
          await activityApi.create(data);
          ElMessage.success('创建成功，等待审核');
        }

        router.push('/activities');
      } catch (error: any) {
        ElMessage.error(error.message || (isEdit.value ? '更新失败' : '创建失败'));
      } finally {
        submitting.value = false;
      }
    }
  });
}

async function loadActivityDetail(id: number) {
  try {
    const activity = await activityApi.getById(id);
    form.title = activity.title;
    form.activityType = activity.activityType;
    form.timeRange = [activity.startTime, activity.endTime];
    form.location = activity.location;
    form.coverImageUrl = activity.coverImageUrl;
    form.maxParticipants = activity.capacity || activity.maxParticipants || 50;
    form.registrationDeadline = activity.registrationDeadline || '';
    form.description = activity.description;
  } catch (error: any) {
    ElMessage.error(error.message || '获取活动详情失败');
    router.push('/activities');
  }
}

// 编辑模式加载数据
onMounted(() => {
  const { id } = route.params;
  if (id) {
    isEdit.value = true;
    activityId.value = Number(id);
    loadActivityDetail(Number(id));
  }
});
</script>

<style scoped lang="scss">
.activity-apply-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
  }
}

.form-section {
  margin-bottom: 24px;
}

.card-header {
  font-weight: 600;
}

.cover-uploader {
  :deep(.el-upload) {
    border: 1px dashed var(--el-border-color);
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: var(--el-transition-duration-fast);

    &:hover {
      border-color: var(--el-color-primary);
    }
  }
}

.cover-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
}

.cover-image {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: cover;
}

.form-tip {
  margin-left: 12px;
  color: #909399;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 24px 0;
}
</style>
