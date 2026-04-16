<template>
  <div class="resource-pool-page">
    <div class="page-header">
      <h2>资源池管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增资源
      </el-button>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ totalResources }}</div>
          <div class="stat-label">总资源数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ availableResources }}</div>
          <div class="stat-label">可用资源</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ maintenanceResources }}</div>
          <div class="stat-label">维护中</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ utilizationRate }}%</div>
          <div class="stat-label">平均利用率</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <el-table :data="resources" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="name" label="资源名称" min-width="200" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="容量" width="100">
          <template #default="{ row }">
            {{ row.capacity }}人
          </template>
        </el-table-column>
        <el-table-column prop="location" label="位置" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="manager" label="负责人" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleSchedule(row)">排期</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑资源' : '新增资源'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="资源名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="资源类型" prop="type">
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="会议室" value="meeting_room" />
            <el-option label="报告厅" value="auditorium" />
            <el-option label="运动场地" value="sports" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="form.capacity" :min="1" :max="1000" />
          <span class="form-tip">人</span>
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input v-model="form.location" />
        </el-form-item>
        <el-form-item label="负责人" prop="manager">
          <el-input v-model="form.manager" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { Plus } from '@element-plus/icons-vue';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage, ElMessageBox } from 'element-plus';
import { formatDateTime, Endpoints, ResourceTypeMap } from '@campus/shared';
import { axiosClient } from '@campus/shared';
import type { Resource } from '@campus/shared';

const loading = ref(false);
const totalResources = ref(0);
const availableResources = ref(0);
const maintenanceResources = ref(0);
const utilizationRate = ref(0);

const resources = ref<Resource[]>([]);

const dialogVisible = ref(false);
const isEdit = ref(false);
const formRef = ref<FormInstance>();
const form = reactive({
  id: null as number | null,
  name: '',
  type: '',
  capacity: 50,
  location: '',
  manager: '',
  remark: '',
});

const rules: FormRules = {
  name: [{ required: true, message: '请输入资源名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择资源类型', trigger: 'change' }],
  capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }],
  location: [{ required: true, message: '请输入位置', trigger: 'blur' }],
};

function getStatusType(status: string) {
  const map: Record<string, string> = {
    available: 'success',
    in_use: 'warning',
    maintenance: 'danger',
  };
  return map[status] || 'info';
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    available: '可用',
    in_use: '使用中',
    maintenance: '维护中',
  };
  return map[status] || status;
}

function handleAdd() {
  isEdit.value = false;
  Object.assign(form, {
    id: null,
    name: '',
    type: '',
    capacity: 50,
    location: '',
    manager: '',
    remark: '',
  });
  dialogVisible.value = true;
}

function handleEdit(row: any) {
  isEdit.value = true;
  Object.assign(form, row);
  dialogVisible.value = true;
}

function handleSchedule(row: any) {
  console.log('排期:', row);
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确定要删除该资源吗？', '提示', { type: 'warning' });
    await axiosClient.apiClient.delete(Endpoints.resources.delete(row.id));
    ElMessage.success('删除成功');
    loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败');
    }
  }
}

async function handleSubmit() {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value && form.id) {
          await axiosClient.apiClient.put(Endpoints.resources.update(form.id), form);
        } else {
          await axiosClient.apiClient.post(Endpoints.resources.create, form);
        }
        ElMessage.success(isEdit.value ? '编辑成功' : '添加成功');
        dialogVisible.value = false;
        loadData();
      } catch (error: any) {
        ElMessage.error(error.message || '保存失败');
      }
    }
  });
}

async function loadData() {
  loading.value = true;
  try {
    const response = await axiosClient.apiClient.get<any>(Endpoints.resources.list);
    resources.value = response?.content || [];
    totalResources.value = resources.value.length;
    availableResources.value = resources.value.filter(r => r.status === 'AVAILABLE').length;
    maintenanceResources.value = resources.value.filter(r => r.status === 'MAINTENANCE').length;
    utilizationRate.value = Math.round(
      (resources.value.filter(r => r.status === 'IN_USE').length / totalResources.value) * 100
    ) || 0;
  } catch (error: any) {
    ElMessage.error(error.message || '获取资源列表失败');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});
</script>

<style scoped lang="scss">
.resource-pool-page {
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

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;

  .stat-value {
    font-size: 32px;
    font-weight: 700;
    color: #409eff;
  }

  .stat-label {
    margin-top: 8px;
    color: #666;
  }
}

.form-tip {
  margin-left: 8px;
  color: #666;
}
</style>
