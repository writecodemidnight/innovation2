<template>
  <div class="resource-apply-page">
    <div class="page-header">
      <h2>资源预约申请</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      class="apply-form"
    >
      <el-card>
        <el-form-item label="关联活动" prop="activityId">
          <el-select v-model="form.activityId" placeholder="选择要预约资源的活动" style="width: 100%">
            <el-option
              v-for="activity in activities"
              :key="activity.id"
              :label="activity.title"
              :value="activity.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="预约资源" prop="resourceId">
          <el-select v-model="form.resourceId" placeholder="选择资源" style="width: 100%">
            <el-option
              v-for="resource in resources"
              :key="resource.id"
              :label="resource.name"
              :value="resource.id"
            >
              <div class="resource-option">
                <span>{{ resource.name }}</span>
                <span class="resource-capacity">容量: {{ resource.capacity }}人</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="预约时间" prop="timeRange">
          <el-date-picker
            v-model="form.timeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="使用人数" prop="attendees">
          <el-input-number v-model="form.attendees" :min="1" :max="500" />
          <span class="form-tip">人</span>
        </el-form-item>

        <el-form-item label="备注说明" prop="remark">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="4"
            placeholder="请输入备注说明（如设备需求、布置要求等）"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            提交申请
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-card>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { FormInstance, FormRules } from 'element-plus';

const router = useRouter();
const formRef = ref<FormInstance>();
const submitting = ref(false);

// 表单数据
const form = reactive({
  activityId: '',
  resourceId: '',
  timeRange: [] as string[],
  attendees: 30,
  remark: '',
});

// 表单验证规则
const rules: FormRules = {
  activityId: [{ required: true, message: '请选择关联活动', trigger: 'change' }],
  resourceId: [{ required: true, message: '请选择预约资源', trigger: 'change' }],
  timeRange: [{ required: true, message: '请选择预约时间', trigger: 'change' }],
  attendees: [{ required: true, message: '请输入使用人数', trigger: 'blur' }],
};

// 活动列表
const activities = ref([
  { id: 1, title: '科技创新讲座' },
  { id: 2, title: '编程工作坊' },
  { id: 3, title: '社团招新活动' },
]);

// 资源列表
const resources = ref([
  { id: 1, name: '学生活动中心301报告厅', capacity: 200 },
  { id: 2, name: '学生活动中心302会议室', capacity: 50 },
  { id: 3, name: '室外篮球场', capacity: 500 },
  { id: 4, name: '礼堂', capacity: 800 },
]);

async function handleSubmit() {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        // TODO: 调用预约API
        const data = {
          activityId: form.activityId,
          resourceId: form.resourceId,
          startTime: form.timeRange[0],
          endTime: form.timeRange[1],
          attendees: form.attendees,
          remark: form.remark,
        };
        console.log('提交数据:', data);

        ElMessage.success('申请提交成功，等待审核');
        router.push('/resources/calendar');
      } finally {
        submitting.value = false;
      }
    }
  });
}

onMounted(() => {
  // TODO: 加载活动和资源列表
});
</script>

<style scoped lang="scss">
.resource-apply-page {
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

.apply-form {
  max-width: 600px;
}

.resource-option {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .resource-capacity {
    color: #909399;
    font-size: 12px;
  }
}

.form-tip {
  margin-left: 12px;
  color: #909399;
}
</style>
