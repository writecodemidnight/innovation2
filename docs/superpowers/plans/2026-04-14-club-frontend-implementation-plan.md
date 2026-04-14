# 社团端前端开发实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成社团端核心功能开发，包括登录认证、活动管理（列表/创建/编辑/删除/详情）对接后端真实API

**Architecture:** 为社团端单独创建axios版本API client，改造user store实现真实登录，创建activityApi封装活动相关接口，保持与现有UI组件复用

**Tech Stack:** Vue 3.4 + Vite 5 + Element Plus 2.5 + axios + Pinia + TypeScript 5.3

**Design Doc:** [2026-04-14-club-frontend-implementation-design.md](../specs/2026-04-14-club-frontend-implementation-design.md)

---

## 文件结构

| 文件 | 操作 | 职责 |
|-----|------|------|
| `packages/shared/src/api/client.axios.ts` | 新增 | axios客户端封装，含拦截器处理token和错误 |
| `packages/shared/src/api/index.ts` | 修改 | 导出axios client供社团端使用 |
| `packages/shared/src/api/types/user.ts` | 修改 | 添加LoginResponse类型定义 |
| `packages/club/src/api/activity.ts` | 新增 | 活动API模块，封装所有活动相关接口 |
| `packages/club/src/stores/user.ts` | 修改 | 改造为真实API登录，添加refreshToken管理 |
| `packages/club/.env.development` | 新增 | 开发环境API基地址配置 |
| `packages/club/src/views/activity/list.vue` | 修改 | 移除模拟数据，对接真实API |
| `packages/club/src/views/activity/apply.vue` | 修改 | 对接创建/更新API，支持编辑模式 |
| `packages/club/src/views/activity/detail.vue` | 修改 | 完善详情页，对接参与者列表API |

---

## Task 1: 创建 axios API Client

**Files:**
- Create: `packages/shared/src/api/client.axios.ts`
- Modify: `packages/shared/src/api/index.ts`

### Step 1: 安装 axios 依赖

- [ ] **安装 axios**

```bash
cd campus-frontend/packages/shared
npm install axios
```

### Step 2: 创建 axios client 文件

- [ ] **创建 `packages/shared/src/api/client.axios.ts`**

```typescript
import axios from 'axios';
import type { ApiResponse } from './types';

// 创建axios实例
const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：添加Authorization头
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：统一错误处理
axiosClient.interceptors.response.use(
  (response) => {
    const data = response.data as ApiResponse<any>;
    if (data.code !== 'SUCCESS' && data.code !== '200') {
      // 业务错误
      const error = new Error(data.message || '请求失败');
      (error as any).code = data.code;
      return Promise.reject(error);
    }
    return data.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，清除并跳转登录
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/club/login';
    }
    return Promise.reject(error);
  }
);

// 导出apiClient
export const apiClient = {
  get: <T>(url: string, config?: any) => axiosClient.get<T>(url, config).then(res => res.data),
  post: <T>(url: string, data?: any, config?: any) => axiosClient.post<T>(url, data, config).then(res => res.data),
  put: <T>(url: string, data?: any, config?: any) => axiosClient.put<T>(url, data, config).then(res => res.data),
  delete: <T>(url: string, config?: any) => axiosClient.delete<T>(url, config).then(res => res.data),
};

export type ApiClient = typeof apiClient;
```

### Step 3: 修改 index.ts 导出 axios client

- [ ] **修改 `packages/shared/src/api/index.ts`**

```typescript
// 导出原uni客户端（供小程序用）
export * from './client';

// 导出axios客户端（供PC端用）
export * from './client.axios';

// 导出类型和端点
export * from './types';
export * from './endpoints';
```

### Step 4: Commit

- [ ] **提交变更**

```bash
git add packages/shared/src/api/
git commit -m "feat: add axios client for club frontend

- Create client.axios.ts with request/response interceptors
- Add token injection and 401 handling
- Export axios client in api/index.ts

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: 添加 LoginResponse 类型

**Files:**
- Modify: `packages/shared/src/api/types/user.ts`

### Step 1: 修改 user.ts 添加 LoginResponse

- [ ] **修改 `packages/shared/src/api/types/user.ts`**，在文件末尾添加：

```typescript
/**
 * 登录响应类型
 * 对应后端 LoginResponse
 */
export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: string;
  user: User;
}
```

### Step 2: Commit

- [ ] **提交变更**

```bash
git add packages/shared/src/api/types/user.ts
git commit -m "feat: add LoginResponse type definition

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: 创建活动 API 模块

**Files:**
- Create: `packages/club/src/api/activity.ts`

### Step 1: 创建 api 目录和 activity.ts

- [ ] **创建 `packages/club/src/api/activity.ts`**

```typescript
import { apiClient } from '@campus/shared';
import { Endpoints } from '@campus/shared';
import type {
  Activity,
  ActivityCreateRequest,
  ActivityListParams,
} from '@campus/shared';

export interface ActivityListResponse {
  content: Activity[];
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
}

export interface ActivityParticipantDto {
  id: number;
  userId: number;
  userName: string;
  avatarUrl?: string;
  status: 'REGISTERED' | 'CHECKED_IN' | 'CANCELLED';
  registeredAt: string;
  checkedInAt?: string;
}

export const activityApi = {
  // 获取活动列表（分页）
  getList: (params: ActivityListParams) =>
    apiClient.get<ActivityListResponse>(Endpoints.activities.list, { params }),

  // 获取活动详情
  getById: (id: number) =>
    apiClient.get<Activity>(Endpoints.activities.detail(id)),

  // 创建活动
  create: (data: ActivityCreateRequest) =>
    apiClient.post<Activity>(Endpoints.activities.create, data),

  // 更新活动
  update: (id: number, data: ActivityCreateRequest) =>
    apiClient.put<Activity>(Endpoints.activities.update(id), data),

  // 删除活动
  delete: (id: number) =>
    apiClient.delete<void>(Endpoints.activities.delete(id)),

  // 提交审批
  submitForApproval: (id: number) =>
    apiClient.post<void>(`${Endpoints.activities.detail(id)}/submit`, {}),

  // 获取参与者列表
  getParticipants: (id: number) =>
    apiClient.get<ActivityParticipantDto[]>(`${Endpoints.activities.list}/${id}/participants`),
};
```

### Step 2: Commit

- [ ] **提交变更**

```bash
git add packages/club/src/api/
git commit -m "feat: add activity API module for club frontend

- Create activityApi with CRUD operations
- Add participant list interface
- Use axios client from shared package

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: 改造 User Store 实现真实登录

**Files:**
- Modify: `packages/club/src/stores/user.ts`

### Step 1: 修改 user.ts 对接真实API

- [ ] **完全替换 `packages/club/src/stores/user.ts`**

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { Endpoints } from '@campus/shared';
import type { User, LoginResponse } from '@campus/shared';

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(localStorage.getItem('access_token') || '');
  const refreshToken = ref<string>(localStorage.getItem('refresh_token') || '');
  const userInfo = ref<User | null>(null);
  const loading = ref(false);

  // Getters
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value);
  const isClubAdmin = computed(() => 
    userInfo.value?.role === 'CLUB_PRESIDENT' || userInfo.value?.role === 'CLUB_MANAGER'
  );
  const isAdmin = computed(() => 
    userInfo.value?.role === 'ADMIN' || userInfo.value?.role === 'SUPER_ADMIN'
  );
  const roleLabel = computed(() => {
    if (!userInfo.value) return '';
    const roleMap: Record<string, string> = {
      'STUDENT': '学生',
      'CLUB_MEMBER': '社团成员',
      'CLUB_MANAGER': '社团管理员',
      'CLUB_PRESIDENT': '社团负责人',
      'ADMIN': '系统管理员',
      'SUPER_ADMIN': '超级管理员',
    };
    return roleMap[userInfo.value.role] || userInfo.value.role;
  });

  // Actions
  const login = async (credentials: { username: string; password: string }) => {
    loading.value = true;
    try {
      const { data } = await axios.post<LoginResponse>(
        Endpoints.auth.wxLogin,
        credentials
      );
      token.value = data.accessToken;
      refreshToken.value = data.refreshToken;
      userInfo.value = data.user;
      localStorage.setItem('access_token', data.accessToken);
      localStorage.setItem('refresh_token', data.refreshToken);
      return true;
    } catch (error: any) {
      console.error('登录失败:', error);
      ElMessage.error(error.response?.data?.message || '登录失败，请检查用户名和密码');
      return false;
    } finally {
      loading.value = false;
    }
  };

  const logout = () => {
    token.value = '';
    refreshToken.value = '';
    userInfo.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  const refreshAccessToken = async () => {
    if (!refreshToken.value) return false;
    try {
      const { data } = await axios.post<LoginResponse>(Endpoints.auth.refresh, {
        refreshToken: refreshToken.value,
      });
      token.value = data.accessToken;
      localStorage.setItem('access_token', data.accessToken);
      return true;
    } catch {
      logout();
      return false;
    }
  };

  const fetchUserInfo = async () => {
    if (!token.value) return;
    // 后续可调用用户信息API
  };

  // 初始化时尝试恢复用户信息（从localStorage的token解析或缓存）
  const initFromStorage = () => {
    const storedToken = localStorage.getItem('access_token');
    const storedRefreshToken = localStorage.getItem('refresh_token');
    if (storedToken) {
      token.value = storedToken;
      refreshToken.value = storedRefreshToken || '';
      // 简化处理：后续可调用 /auth/profile 获取完整用户信息
      // 暂时标记为已登录，详情页加载时再获取
      userInfo.value = { id: 0, role: 'CLUB_MEMBER' } as User;
    }
  };

  return {
    token,
    refreshToken,
    userInfo,
    loading,
    isLoggedIn,
    isClubAdmin,
    isAdmin,
    roleLabel,
    login,
    logout,
    refreshAccessToken,
    fetchUserInfo,
    initFromStorage,
  };
});
```

### Step 2: Commit

- [ ] **提交变更**

```bash
git add packages/club/src/stores/user.ts
git commit -m "feat: refactor user store with real API integration

- Replace mock login with real axios API call
- Add refreshToken management
- Add error handling with ElMessage
- Add initFromStorage for page refresh recovery

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: 添加环境变量配置

**Files:**
- Create: `packages/club/.env.development`

### Step 1: 创建开发环境配置

- [ ] **创建 `packages/club/.env.development`**

```bash
# API基地址
VITE_API_BASE_URL=http://localhost:8080/api/v1

# 应用环境
VITE_APP_ENV=development

# 应用标题
VITE_APP_TITLE=社团管理系统
```

### Step 2: Commit

- [ ] **提交变更**

```bash
git add packages/club/.env.development
git commit -m "chore: add development environment config

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: 改造活动列表页对接真实API

**Files:**
- Modify: `packages/club/src/views/activity/list.vue`

### Step 1: 修改导入和活动状态映射

- [ ] **修改 `packages/club/src/views/activity/list.vue`**

找到 `<script setup>` 部分，修改导入和逻辑：

```typescript
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Search, Plus, ArrowDown } from '@element-plus/icons-vue';
import { formatDateTime, ActivityStatusMap, ActivityTypeMap } from '@campus/shared';
import { activityApi } from '@/api/activity';
import type { Activity } from '@campus/shared';
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
const activities = ref<Activity[]>([]);

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
  return ActivityStatusMap[status as keyof typeof ActivityStatusMap] || status;
}

function getActivityTypeLabel(type: string) {
  return ActivityTypeMap[type as keyof typeof ActivityTypeMap] || type;
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
  router.push(`/activities/${row.id}/edit`);
}

function handleView(row: Activity) {
  router.push(`/activities/${row.id}`);
}

function handleReport(row: Activity) {
  router.push(`/reports/radar?activityId=${row.id}`);
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
```

### Step 2: 更新模板中的字段

- [ ] **修改模板中的字段映射**

原 `row.activityType` 改为直接使用，原 `row.coverImageUrl` 需要处理可能为空的情况：

```vue
<el-table-column prop="title" label="活动名称" min-width="200">
  <template #default="{ row }">
    <div class="activity-name">
      <el-avatar :size="40" :src="row.coverImageUrl || '/default-activity.png'" shape="square" />
      <div class="name-info">
        <div class="title">{{ row.title }}</div>
        <div class="type">{{ getActivityTypeLabel(row.activityType) }}</div>
      </div>
    </div>
  </template>
</el-table-column>
```

### Step 3: Commit

- [ ] **提交变更**

```bash
git add packages/club/src/views/activity/list.vue
git commit -m "feat: integrate activity list with real API

- Replace mock data with activityApi.getList
- Add error handling with ElMessage
- Update field mappings for backend response
- Add loading states

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 7: 改造活动申请表单对接真实API

**Files:**
- Modify: `packages/club/src/views/activity/apply.vue`

### Step 1: 修改导入和逻辑

- [ ] **修改 `packages/club/src/views/activity/apply.vue`** 的 script setup 部分：

```typescript
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Plus } from '@element-plus/icons-vue';
import { ActivityType, ActivityTypeMap } from '@campus/shared';
import { activityApi } from '@/api/activity';
import { useUserStore } from '@/stores/user';
import type { ActivityCreateRequest } from '@campus/shared';
import type { FormInstance, FormRules, UploadProps } from 'element-plus';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const formRef = ref<FormInstance>();
const submitting = ref(false);
const isEdit = ref(false);
const activityId = ref<number | null>(null);

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
  title: [{ required: true, message: '请输入活动标题', trigger: 'blur' }],
  activityType: [{ required: true, message: '请选择活动类型', trigger: 'change' }],
  timeRange: [{ required: true, message: '请选择活动时间', trigger: 'change' }],
  location: [{ required: true, message: '请输入活动地点', trigger: 'blur' }],
  maxParticipants: [{ required: true, message: '请设置人数限制', trigger: 'blur' }],
  description: [{ required: true, message: '请输入活动描述', trigger: 'blur' }],
};

// 上传相关
const handleUploadSuccess: UploadProps['onSuccess'] = (response) => {
  form.coverImageUrl = response.url;
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
          clubId: userStore.userInfo?.clubId || 1,
          activityType: form.activityType as ActivityType,
          startTime: form.timeRange[0],
          endTime: form.timeRange[1],
          location: form.location,
          maxParticipants: form.maxParticipants,
          coverImageUrl: form.coverImageUrl,
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

// 加载活动详情（编辑模式）
async function loadActivityDetail(id: number) {
  try {
    const activity = await activityApi.getById(id);
    form.title = activity.title;
    form.activityType = activity.activityType;
    form.timeRange = [activity.startTime, activity.endTime];
    form.location = activity.location;
    form.coverImageUrl = activity.coverImageUrl;
    form.maxParticipants = activity.maxParticipants;
    form.description = activity.description;
  } catch (error: any) {
    ElMessage.error(error.message || '获取活动详情失败');
    router.push('/activities');
  }
}

// 编辑模式加载数据
onMounted(() => {
  const id = route.params.id;
  if (id) {
    isEdit.value = true;
    activityId.value = Number(id);
    loadActivityDetail(Number(id));
  }
});
```

### Step 2: 更新页面标题

- [ ] **修改模板中的页面标题**

```vue
<div class="page-header">
  <h2>{{ isEdit ? '编辑活动' : '新建活动' }}</h2>
  <el-button @click="$router.back()">返回</el-button>
</div>
```

### Step 3: Commit

- [ ] **提交变更**

```bash
git add packages/club/src/views/activity/apply.vue
git commit -m "feat: integrate activity apply form with real API

- Add activityApi.create and activityApi.update integration
- Support edit mode with data loading
- Add clubId from user store
- Add error handling with ElMessage

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 8: 完善活动详情页

**Files:**
- Modify: `packages/club/src/views/activity/detail.vue`

### Step 1: 读取当前详情页内容

- [ ] **先读取现有详情页文件**

```bash
cat packages/club/src/views/activity/detail.vue
```

（根据现有内容决定是否需要完全重写或部分修改）

### Step 2: 创建/修改详情页

- [ ] **更新详情页完整代码**

如果文件不存在或需要重写，创建完整的详情页：

```vue
<template>
  <div class="activity-detail-page">
    <div class="page-header">
      <h2>活动详情</h2>
      <div class="header-actions">
        <el-button @click="$router.back()">返回</el-button>
        <el-button type="primary" @click="handleEdit">编辑</el-button>
        <el-button type="success" @click="handleSubmit" v-if="activity?.status === 'PLANNING'">
          提交审核
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：活动信息 -->
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

      <!-- 右侧：参与者列表 -->
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
import { formatDateTime, ActivityStatusMap, ActivityTypeMap } from '@campus/shared';
import { activityApi, type ActivityParticipantDto } from '@/api/activity';
import type { Activity } from '@campus/shared';
import { ElMessage, ElMessageBox } from 'element-plus';

const route = useRoute();
const router = useRouter();

const activity = ref<Activity | null>(null);
const participants = ref<ActivityParticipantDto[]>([]);
const loading = ref(false);
const participantsLoading = ref(false);

function getStatusType(status?: string) {
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
  return map[status || ''] || 'info';
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
  try {
    activity.value = await activityApi.getById(id);
    loadParticipants(id);
  } catch (error: any) {
    ElMessage.error(error.message || '获取活动详情失败');
  } finally {
    loading.value = false;
  }
}

async function loadParticipants(activityId: number) {
  participantsLoading.value = true;
  try {
    participants.value = await activityApi.getParticipants(activityId);
  } catch (error: any) {
    console.error('获取参与者失败:', error);
  } finally {
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
```

### Step 3: Commit

- [ ] **提交变更**

```bash
git add packages/club/src/views/activity/detail.vue
git commit -m "feat: complete activity detail page with API integration

- Add activityApi.getById for detail loading
- Add activityApi.getParticipants for participant list
- Add activityApi.submitForApproval for submission
- Add status display and action buttons

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 9: 更新路由支持编辑页面

**Files:**
- Modify: `packages/club/src/router/index.ts`

### Step 1: 添加编辑活动路由

- [ ] **修改 `packages/club/src/router/index.ts`**，在 activities/apply 路由后添加：

```typescript
{
  path: 'activities/:id/edit',
  name: 'ActivityEdit',
  component: () => import('@/views/activity/apply.vue'),
  meta: { title: '编辑活动', hidden: true },
},
```

### Step 2: Commit

- [ ] **提交变更**

```bash
git add packages/club/src/router/index.ts
git commit -m "feat: add edit activity route

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 10: 联调测试

**Files:** 多个文件

### Step 1: 启动后端服务

- [ ] **确保后端服务运行在 http://localhost:8080**

```bash
cd campus-main
mvn spring-boot:run
```

### Step 2: 启动社团端开发服务器

- [ ] **启动前端开发服务器**

```bash
cd campus-frontend/packages/club
npm run dev
```

### Step 3: 验证登录功能

- [ ] **测试登录流程**

1. 访问 http://localhost:5173/club/login
2. 输入用户名密码（使用后端配置的测试账号）
3. 验证：
   - 登录成功后跳转到首页
   - localStorage 中有 access_token 和 refresh_token
   - 页面显示用户信息

### Step 4: 验证活动列表

- [ ] **测试活动列表**

1. 进入活动列表页面
2. 验证：
   - 正确显示后端返回的活动数据
   - 分页功能正常
   - 搜索功能正常
   - 筛选功能正常

### Step 5: 验证活动创建

- [ ] **测试活动创建**

1. 点击"新建活动"
2. 填写表单并提交
3. 验证：
   - 创建成功后跳转列表页
   - 新创建的活动显示在列表中

### Step 6: 验证活动编辑

- [ ] **测试活动编辑**

1. 点击活动列表的"编辑"按钮
2. 修改表单内容并提交
3. 验证：
   - 数据正确回填
   - 更新成功后列表显示最新数据

### Step 7: 验证活动删除

- [ ] **测试活动删除**

1. 点击活动列表的"更多"->"删除"
2. 确认删除
3. 验证：
   - 删除成功后列表自动刷新
   - 被删除的活动不再显示

### Step 8: 验证活动详情

- [ ] **测试活动详情**

1. 点击活动列表的"详情"
2. 验证：
   - 正确显示活动详细信息
   - 参与者列表正确显示
   - 提交审核按钮可用（针对策划中状态的活动）

### Step 9: 最终 Commit

- [ ] **提交所有变更**

```bash
git add .
git commit -m "feat: complete club frontend core features

- Add axios client with token management
- Integrate real API for authentication
- Complete activity CRUD operations
- Add activity detail with participants
- Add submit for approval feature

All core features tested and working.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 验收检查清单

- [ ] axios client 正确添加 Authorization 头
- [ ] 401 错误时自动跳转登录页
- [ ] 登录成功存储 access_token 和 refresh_token
- [ ] 活动列表分页、搜索、筛选功能正常
- [ ] 创建活动成功后出现在列表中
- [ ] 编辑活动数据正确回填
- [ ] 删除活动后列表自动刷新
- [ ] 活动详情页显示完整信息
- [ ] 参与者列表正确显示
- [ ] 提交审批功能正常
- [ ] 所有 API 错误正确处理并提示用户

---

## 常见问题

**Q: axios 报错找不到模块？**
A: 确保在 `packages/shared` 目录下运行 `npm install axios`

**Q: 跨域错误？**
A: 检查后端是否正确配置了 CORS，允许前端域名访问

**Q: 401 错误但已登录？**
A: 检查 token 是否正确存储到 localStorage，axios 拦截器是否正确读取

**Q: 活动列表为空？**
A: 确认后端有数据，检查 API 响应格式是否与预期一致

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-14-club-frontend-implementation-plan.md`.**
