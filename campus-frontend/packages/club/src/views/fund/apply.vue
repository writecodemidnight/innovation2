<template>
  <div class="fund-apply-page">
    <div class="page-header">
      <h2>资金申请</h2>
      <el-button @click="$router.back()">返回</el-button>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      class="apply-form"
    >
      <el-card v-loading="loading">
        <el-form-item label="关联活动" prop="activityId">
          <el-select
            v-model="form.activityId"
            placeholder="选择要申请资金的活动（可选）"
            style="width: 100%"
            clearable
            :loading="activityLoading"
          >
            <el-option
              v-for="activity in activities"
              :key="activity.id"
              :label="activity.title"
              :value="activity.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="申请金额" prop="amount">
          <el-input-number
            v-model="form.amount"
            :min="100"
            :max="100000"
            :precision="2"
            :step="100"
            style="width: 200px"
          />
          <span class="form-tip">元</span>
        </el-form-item>

        <el-form-item label="资金用途" prop="purpose">
          <el-input
            v-model="form.purpose"
            type="textarea"
            :rows="4"
            placeholder="请详细说明资金用途，包括具体支出项目"
          />
        </el-form-item>

        <el-form-item label="预算明细" prop="budgetBreakdown">
          <el-input
            v-model="form.budgetBreakdown"
            type="textarea"
            :rows="6"
            placeholder="请提供预算明细，格式如下：
场地租赁：2000元
设备租赁：1500元
宣传材料：500元
..."
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
import { ElMessage } from 'element-plus';
import { activityApi } from '@/api/activity';
import { fundApi } from '@/api/fund';
import type { Activity } from '@campus/shared';

const router = useRouter();
const formRef = ref<FormInstance>();
const loading = ref(false);
const submitting = ref(false);
const activityLoading = ref(false);

// 表单数据
const form = reactive({
  activityId: undefined as number | undefined,
  amount: 1000,
  purpose: '',
  budgetBreakdown: '',
});

// 表单验证规则
const rules: FormRules = {
  amount: [
    { required: true, message: '请输入申请金额', trigger: 'blur' },
    { type: 'number', min: 100, message: '金额至少为100元', trigger: 'blur' },
  ],
  purpose: [
    { required: true, message: '请输入资金用途', trigger: 'blur' },
    { min: 10, message: '用途说明至少10个字符', trigger: 'blur' },
  ],
  budgetBreakdown: [
    { required: true, message: '请输入预算明细', trigger: 'blur' },
    { min: 20, message: '预算明细至少20个字符', trigger: 'blur' },
  ],
};

// 活动列表
const activities = ref<Activity[]>([]);

// 加载活动列表
async function loadActivities() {
  activityLoading.value = true;
  try {
    const response = await activityApi.getList({
      page: 0,
      size: 100,
    });
    activities.value = response.content || [];
  } catch (error: any) {
    ElMessage.error(error.message || '获取活动列表失败');
  } finally {
    activityLoading.value = false;
  }
}

async function handleSubmit() {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        await fundApi.apply({
          activityId: form.activityId,
          amount: form.amount,
          purpose: form.purpose,
          budgetBreakdown: form.budgetBreakdown,
        });
        ElMessage.success('申请提交成功，等待审核');
        router.push('/funds');
      } catch (error: any) {
        ElMessage.error(error.message || '申请提交失败');
      } finally {
        submitting.value = false;
      }
    }
  });
}

onMounted(() => {
  loadActivities();
});
</script>

<style scoped lang="scss">
.fund-apply-page {
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

.form-tip {
  margin-left: 12px;
  color: #909399;
}
</style>
