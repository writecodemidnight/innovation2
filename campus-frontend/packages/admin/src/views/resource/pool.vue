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
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: rgba(0, 212, 170, 0.1)">
            <el-icon size="24" color="#00d4aa"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #00d4aa">{{ resourceStore.stats?.totalResources || 0 }}</div>
            <div class="stat-label">总资源数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: rgba(88, 166, 255, 0.1)">
            <el-icon size="24" color="#58a6ff"><Check /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #58a6ff">{{ resourceStore.stats?.statusDistribution?.AVAILABLE || 0 }}</div>
            <div class="stat-label">可用资源</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: rgba(240, 136, 62, 0.1)">
            <el-icon size="24" color="#f0883e"><Warning /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #f0883e">{{ resourceStore.stats?.statusDistribution?.MAINTENANCE || 0 }}</div>
            <div class="stat-label">维护中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: rgba(163, 113, 247, 0.1)">
            <el-icon size="24" color="#a371f7"><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #a371f7">{{ Math.round(((resourceStore.stats?.statusDistribution?.IN_USE || 0) / (resourceStore.stats?.totalResources || 1)) * 100) }}%</div>
            <div class="stat-label">平均利用率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <div class="filter-bar">
        <el-select v-model="filterType" placeholder="资源类型" clearable style="width: 150px">
          <el-option label="场地" value="场地" />
          <el-option label="设备" value="设备" />
          <el-option label="会议室" value="会议室" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 150px">
          <el-option label="可用" value="AVAILABLE" />
          <el-option label="使用中" value="IN_USE" />
          <el-option label="维护中" value="MAINTENANCE" />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <el-table :data="resourceStore.resources" v-loading="resourceStore.loading" style="width: 100%">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="name" label="资源名称" min-width="180" />
        <el-table-column prop="resourceType" label="类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.resourceType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="容量" width="100">
          <template #default="{ row }">
            {{ row.capacity }}人
          </template>
        </el-table-column>
        <el-table-column prop="location" label="位置" min-width="150" />
        <el-table-column prop="manager" label="负责人" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑资源' : '新增资源'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="资源名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入资源名称" />
        </el-form-item>
        <el-form-item label="资源类型" prop="resourceType">
          <el-select v-model="form.resourceType" style="width: 100%" placeholder="请选择资源类型">
            <el-option label="场地" value="场地" />
            <el-option label="设备" value="设备" />
            <el-option label="会议室" value="会议室" />
          </el-select>
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="form.capacity" :min="1" :max="1000" style="width: 150px" />
          <span class="form-tip">人</span>
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input v-model="form.location" placeholder="请输入资源位置" />
        </el-form-item>
        <el-form-item label="负责人" prop="manager">
          <el-input v-model="form.manager" placeholder="请输入负责人姓名" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" style="width: 100%" placeholder="请选择状态">
            <el-option label="可用" value="AVAILABLE" />
            <el-option label="使用中" value="IN_USE" />
            <el-option label="维护中" value="MAINTENANCE" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { Plus, OfficeBuilding, Check, Warning, TrendCharts, Search } from '@element-plus/icons-vue';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useResourceStore } from '@/stores';

const resourceStore = useResourceStore();

const filterType = ref('');
const filterStatus = ref('');
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);

const dialogVisible = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const formRef = ref<FormInstance>();
const form = reactive({
  id: null as number | null,
  name: '',
  resourceType: '',
  capacity: 50,
  location: '',
  manager: '',
  status: 'AVAILABLE',
  remark: '',
});

const rules: FormRules = {
  name: [{ required: true, message: '请输入资源名称', trigger: 'blur' }],
  resourceType: [{ required: true, message: '请选择资源类型', trigger: 'change' }],
  capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }],
  location: [{ required: true, message: '请输入位置', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
};

function getStatusType(status: string) {
  const map: Record<string, string> = {
    AVAILABLE: 'success',
    IN_USE: 'warning',
    MAINTENANCE: 'danger',
  };
  return map[status] || 'info';
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    AVAILABLE: '可用',
    IN_USE: '使用中',
    MAINTENANCE: '维护中',
  };
  return map[status] || status;
}

function handleSearch() {
  page.value = 1;
  loadData();
}

function handleReset() {
  filterType.value = '';
  filterStatus.value = '';
  page.value = 1;
  loadData();
}

function handleSizeChange(size: number) {
  pageSize.value = size;
  loadData();
}

function handlePageChange(current: number) {
  page.value = current;
  loadData();
}

function handleAdd() {
  isEdit.value = false;
  Object.assign(form, {
    id: null,
    name: '',
    resourceType: '',
    capacity: 50,
    location: '',
    manager: '',
    status: 'AVAILABLE',
    remark: '',
  });
  dialogVisible.value = true;
}

function handleEdit(row: any) {
  isEdit.value = true;
  Object.assign(form, row);
  dialogVisible.value = true;
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确定要删除该资源吗？', '提示', { type: 'warning' });
    await resourceStore.deleteResource(row.id);
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
      submitting.value = true;
      try {
        const data = {
          name: form.name,
          resourceType: form.resourceType,
          capacity: form.capacity,
          location: form.location,
          manager: form.manager,
          status: form.status,
          remark: form.remark,
        };
        if (isEdit.value && form.id) {
          await resourceStore.updateResource(form.id, data);
        } else {
          await resourceStore.createResource(data);
        }
        ElMessage.success(isEdit.value ? '编辑成功' : '添加成功');
        dialogVisible.value = false;
        loadData();
      } catch (error: any) {
        ElMessage.error(error.message || '保存失败');
      } finally {
        submitting.value = false;
      }
    }
  });
}

async function loadData() {
  const response = await resourceStore.fetchResources(page.value - 1, pageSize.value, filterType.value || undefined, filterStatus.value || undefined);
  total.value = response.totalElements || 0;
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

onMounted(() => {
  resourceStore.fetchStats();
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
    color: #c9d1d9;
  }
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;

  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 12px;
  }

  .stat-value {
    font-size: 24px;
    font-weight: 700;
    line-height: 1.2;
  }

  .stat-label {
    font-size: 13px;
    color: #8b949e;
    margin-top: 4px;
  }
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.form-tip {
  margin-left: 8px;
  color: #666;
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
</style>
