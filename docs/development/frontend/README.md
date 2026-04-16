# 前端开发指南

本文档介绍前端项目的开发规范和最佳实践。

---

## 目录

1. [项目结构](#项目结构)
2. [开发规范](#开发规范)
3. [组件开发](#组件开发)
4. [状态管理](#状态管理)
5. [API 调用](#api-调用)
6. [性能优化](#性能优化)

---

## 项目结构

```
campus-frontend/
├── packages/
│   ├── shared/                    # 共享包
│   │   ├── src/
│   │   │   ├── api/              # API 类型定义
│   │   │   │   ├── types/        # 数据类型
│   │   │   │   └── client.axios.ts
│   │   │   ├── utils/            # 工具函数
│   │   │   └── constants/        # 常量
│   │   └── package.json
│   │
│   ├── club/                      # 社团端
│   │   ├── src/
│   │   │   ├── api/              # API 模块
│   │   │   ├── components/       # 公共组件
│   │   │   ├── composables/      # 组合式函数
│   │   │   ├── layouts/          # 布局
│   │   │   ├── router/           # 路由
│   │   │   ├── stores/           # Pinia 状态
│   │   │   ├── styles/           # 样式
│   │   │   ├── views/            # 页面
│   │   │   └── App.vue
│   │   └── package.json
│   │
│   ├── admin/                     # 管理端
│   └── student/                   # 学生端(uni-app)
│
├── package.json
└── pnpm-workspace.yaml
```

---

## 开发规范

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件 | PascalCase | `ActivityCard.vue` |
| 组合式函数 | camelCase + use | `useActivity.ts` |
| 工具函数 | camelCase | `formatDate.ts` |
| 常量 | SNAKE_CASE | `API_BASE_URL` |
| 类型 | PascalCase | `ActivityDTO` |
| 枚举 | PascalCase | `ActivityStatus` |
| 文件 | camelCase 或 kebab-case | `activity-list.vue` |

### TypeScript 规范

```typescript
// 定义类型
interface Activity {
  id: number;
  title: string;
  status: ActivityStatus;
  startTime: string;
}

// 枚举定义
enum ActivityStatus {
  DRAFT = 'DRAFT',
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  ONGOING = 'ONGOING',
  COMPLETED = 'COMPLETED'
}

// 函数必须有返回类型
function formatDate(date: string | Date, format = 'YYYY-MM-DD'): string {
  return dayjs(date).format(format);
}

// Props 定义
interface ActivityCardProps {
  activity: Activity;
  showActions?: boolean;
  onRegister?: (id: number) => void;
}
```

### Vue 组件规范

```vue
<script setup lang="ts">
/**
 * 活动卡片组件
 * @description 展示活动基本信息，支持报名操作
 * @author Team
 */

import { computed } from 'vue';
import type { Activity } from '@campus/shared';
import { ActivityStatus } from '@campus/shared';

// Props 定义
interface Props {
  activity: Activity;
  showActions?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true
});

// Emits 定义
const emit = defineEmits<{
  register: [id: number];
  view: [id: number];
}>();

// 计算属性
const statusText = computed(() => {
  const map: Record<ActivityStatus, string> = {
    [ActivityStatus.DRAFT]: '草稿',
    [ActivityStatus.PENDING]: '待审批',
    [ActivityStatus.APPROVED]: '已通过',
    [ActivityStatus.ONGOING]: '进行中',
    [ActivityStatus.COMPLETED]: '已结束'
  };
  return map[props.activity.status];
});

const statusType = computed(() => {
  const map: Record<ActivityStatus, string> = {
    [ActivityStatus.DRAFT]: 'info',
    [ActivityStatus.PENDING]: 'warning',
    [ActivityStatus.APPROVED]: 'success',
    [ActivityStatus.ONGOING]: 'primary',
    [ActivityStatus.COMPLETED]: ''
  };
  return map[props.activity.status];
});

// 方法
function handleRegister() {
  emit('register', props.activity.id);
}

function handleView() {
  emit('view', props.activity.id);
}
</script>

<template>
  <el-card class="activity-card" shadow="hover">
    <div class="activity-header">
      <h3 class="title" @click="handleView">{{ activity.title }}</h3>
      <el-tag :type="statusType">{{ statusText }}</el-tag>
    </div>
    
    <div class="activity-info">
      <p><el-icon><Calendar /></el-icon> {{ formatDate(activity.startTime) }}</p>
      <p><el-icon><Location /></el-icon> {{ activity.location }}</p>
    </div>
    
    <div v-if="showActions" class="activity-actions">
      <el-button 
        type="primary" 
        :disabled="activity.status !== ActivityStatus.APPROVED"
        @click="handleRegister"
      >
        立即报名
      </el-button>
      <el-button @click="handleView">查看详情</el-button>
    </div>
  </el-card>
</template>

<style scoped lang="scss">
.activity-card {
  margin-bottom: 16px;
  
  .activity-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    .title {
      margin: 0;
      font-size: 16px;
      cursor: pointer;
      
      &:hover {
        color: var(--el-color-primary);
      }
    }
  }
  
  .activity-info {
    color: var(--el-text-color-regular);
    font-size: 14px;
    
    p {
      margin: 8px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
  
  .activity-actions {
    margin-top: 16px;
    display: flex;
    gap: 8px;
  }
}
</style>
```

---

## 组件开发

### 1. 公共组件

**文件**: `packages/club/src/components/ActivityCard.vue`

```vue
<script setup lang="ts">
import { computed } from 'vue';
import type { Activity } from '@campus/shared';

interface Props {
  activity: Activity;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
});

const emit = defineEmits<{
  click: [id: number];
}>();

const isOngoing = computed(() => props.activity.status === 'ONGOING');
</script>

<template>
  <el-skeleton :rows="3" :loading="loading" animated>
    <template #default>
      <div class="activity-card" @click="emit('click', activity.id)">
        <!-- 组件内容 -->
      </div>
    </template>
  </el-skeleton>
</template>
```

### 2. 组合式函数

**文件**: `packages/club/src/composables/useActivity.ts`

```typescript
import { ref, computed } from 'vue';
import type { Activity, ActivityQueryParams } from '@campus/shared';
import { activityApi } from '@/api/activity';

export function useActivity() {
  // 状态
  const activities = ref<Activity[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const pagination = ref({
    page: 0,
    size: 10,
    total: 0
  });

  // 计算属性
  const hasMore = computed(() => {
    return pagination.value.page * pagination.value.size < pagination.value.total;
  });

  // 方法
  async function fetchActivities(params?: ActivityQueryParams) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await activityApi.getList({
        page: pagination.value.page,
        size: pagination.value.size,
        ...params
      });
      
      activities.value = response.data.content;
      pagination.value.total = response.data.totalElements;
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取活动列表失败';
    } finally {
      loading.value = false;
    }
  }

  async function loadMore() {
    if (!hasMore.value || loading.value) return;
    
    pagination.value.page++;
    await fetchActivities();
  }

  return {
    activities,
    loading,
    error,
    pagination,
    hasMore,
    fetchActivities,
    loadMore
  };
}
```

---

## 状态管理

### Pinia Store

**文件**: `packages/club/src/stores/activity.ts`

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Activity, ActivityDetail } from '@campus/shared';
import { activityApi } from '@/api/activity';

export const useActivityStore = defineStore('activity', () => {
  // State
  const activities = ref<Activity[]>([]);
  const currentActivity = ref<ActivityDetail | null>(null);
  const loading = ref(false);
  
  // Getters
  const ongoingActivities = computed(() => 
    activities.value.filter(a => a.status === 'ONGOING')
  );
  
  const myActivities = computed(() => 
    activities.value.filter(a => a.isRegistered)
  );

  // Actions
  async function fetchActivityList(params?: Record<string, unknown>) {
    loading.value = true;
    try {
      const response = await activityApi.getList(params);
      activities.value = response.data.content;
      return response.data;
    } finally {
      loading.value = false;
    }
  }

  async function fetchActivityDetail(id: number) {
    loading.value = true;
    try {
      const response = await activityApi.getDetail(id);
      currentActivity.value = response.data;
      return response.data;
    } finally {
      loading.value = false;
    }
  }

  async function createActivity(data: CreateActivityRequest) {
    const response = await activityApi.create(data);
    activities.value.unshift(response.data);
    return response.data;
  }

  function clearCurrentActivity() {
    currentActivity.value = null;
  }

  return {
    activities,
    currentActivity,
    loading,
    ongoingActivities,
    myActivities,
    fetchActivityList,
    fetchActivityDetail,
    createActivity,
    clearCurrentActivity
  };
});
```

---

## API 调用

### API 模块

**文件**: `packages/club/src/api/activity.ts`

```typescript
import { apiClient } from '@campus/shared';
import type { 
  Activity, 
  ActivityDetail, 
  CreateActivityRequest,
  ActivityQueryParams,
  ApiResponse,
  PageResponse 
} from '@campus/shared';

export const activityApi = {
  /**
   * 获取活动列表
   */
  getList(params?: ActivityQueryParams) {
    return apiClient.get<ApiResponse<PageResponse<Activity>>>('/api/v1/activities', { 
      params 
    });
  },

  /**
   * 获取活动详情
   */
  getDetail(id: number) {
    return apiClient.get<ApiResponse<ActivityDetail>>(`/api/v1/activities/${id}`);
  },

  /**
   * 创建活动
   */
  create(data: CreateActivityRequest) {
    return apiClient.post<ApiResponse<Activity>>('/api/v1/activities', data);
  },

  /**
   * 更新活动
   */
  update(id: number, data: Partial<CreateActivityRequest>) {
    return apiClient.put<ApiResponse<Activity>>(`/api/v1/activities/${id}`, data);
  },

  /**
   * 删除活动
   */
  delete(id: number) {
    return apiClient.delete<ApiResponse<void>>(`/api/v1/activities/${id}`);
  },

  /**
   * 报名活动
   */
  register(id: number) {
    return apiClient.post<ApiResponse<void>>(`/api/v1/activities/${id}/register`);
  },

  /**
   * 取消报名
   */
  cancelRegistration(id: number) {
    return apiClient.post<ApiResponse<void>>(`/api/v1/activities/${id}/cancel`);
  }
};
```

### 请求拦截器

**文件**: `packages/shared/src/api/client.axios.ts`

```typescript
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import { useUserStore } from '@/stores/user';

// 创建实例
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加时间戳防止缓存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      };
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 直接返回数据
    return response.data;
  },
  (error: AxiosError<ApiError>) => {
    const { response } = error;
    
    if (response) {
      switch (response.status) {
        case 401:
          // Token过期，清除登录状态
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
          
        case 403:
          ElMessage.error('没有权限执行此操作');
          break;
          
        case 404:
          ElMessage.error('请求的资源不存在');
          break;
          
        case 500:
          ElMessage.error('服务器错误，请稍后重试');
          break;
          
        default:
          ElMessage.error(response.data?.message || '请求失败');
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接');
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

## 性能优化

### 1. 组件懒加载

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/activities',
    component: () => import('@/views/activity/list.vue'),
    meta: { 
      title: '活动列表',
      keepAlive: true 
    }
  },
  {
    path: '/activities/:id',
    component: () => import('@/views/activity/detail.vue'),
    meta: { title: '活动详情' }
  }
];

export const router = createRouter({
  history: createWebHistory(),
  routes
});
```

### 2. 虚拟列表

```vue
<script setup lang="ts">
import { ref, computed } from 'vue';
import { useVirtualList } from '@vueuse/core';

const allActivities = ref<Activity[]>([]);

const { list, containerProps, wrapperProps } = useVirtualList(
  allActivities,
  {
    itemHeight: 120,
    overscan: 10
  }
);
</script>

<template>
  <div v-bind="containerProps" class="activity-list">
    <div v-bind="wrapperProps">
      <ActivityCard
        v-for="{ data, index } in list"
        :key="data.id"
        :activity="data"
        :style="{ height: '120px' }"
      />
    </div>
  </div>
</template>
```

### 3. 防抖节流

```typescript
import { ref } from 'vue';
import { useDebounceFn, useThrottleFn } from '@vueuse/core';

// 搜索防抖
const searchQuery = ref('');

const debouncedSearch = useDebounceFn(async (query: string) => {
  const results = await activityApi.search(query);
  searchResults.value = results.data;
}, 300);

// 滚动节流
const throttledScroll = useThrottleFn(() => {
  checkScrollPosition();
}, 100);

window.addEventListener('scroll', throttledScroll);
```

### 4. 图片优化

```vue
<template>
  <el-image
    :src="activity.posterUrl"
    :preview-src-list="[activity.posterUrl]"
    lazy
    fit="cover"
  >
    <template #placeholder>
      <div class="image-placeholder">
        <el-icon><Picture /></el-icon>
      </div>
    </template>
    <template #error>
      <div class="image-error">
        <el-icon><Picture /></el-icon>
      </div>
    </template>
  </el-image>
</template>
```

---

## 错误处理

### 全局错误边界

```typescript
// main.ts
import { createApp } from 'vue';
import App from './App.vue';

const app = createApp(App);

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('全局错误:', err);
  console.error('组件:', vm);
  console.error('信息:', info);
  
  // 上报到监控系统
  reportError({
    error: err,
    component: vm?.$options?.name,
    info,
    timestamp: Date.now()
  });
};

app.mount('#app');
```

### 请求错误处理

```typescript
async function handleSubmit() {
  try {
    await activityApi.create(formData);
    ElMessage.success('创建成功');
    router.back();
  } catch (error) {
    if (error.response?.data?.code === 'VALIDATION_ERROR') {
      // 表单验证错误
      const errors = error.response.data.errors;
      Object.entries(errors).forEach(([field, message]) => {
        formErrors[field] = message;
      });
    } else {
      ElMessage.error(error.message || '创建失败');
    }
  }
}
```

---

## 测试

### 组件测试

```typescript
// tests/components/ActivityCard.spec.ts
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import ActivityCard from '@/components/ActivityCard.vue';

describe('ActivityCard', () => {
  const mockActivity = {
    id: 1,
    title: '测试活动',
    status: 'ONGOING',
    startTime: '2024-04-15T10:00:00',
    location: '教学楼A101'
  };

  it('renders activity title', () => {
    const wrapper = mount(ActivityCard, {
      props: { activity: mockActivity }
    });
    
    expect(wrapper.text()).toContain('测试活动');
  });

  it('emits click event when clicked', async () => {
    const wrapper = mount(ActivityCard, {
      props: { activity: mockActivity }
    });
    
    await wrapper.find('.activity-card').trigger('click');
    
    expect(wrapper.emitted('click')).toBeTruthy();
    expect(wrapper.emitted('click')[0]).toEqual([1]);
  });
});
```
