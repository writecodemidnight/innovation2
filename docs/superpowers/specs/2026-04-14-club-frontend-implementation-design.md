# 社团端前端开发设计文档

## 项目信息

- **日期**: 2026-04-14
- **目标**: 完成社团端（Vue3 + Element Plus）核心功能开发
- **方案**: 方案A（最小改动，为社团端单独创建axios版本API client）

---

## 1. 设计目标

为社团端完成以下核心功能：

| 优先级 | 功能模块 | 目标 |
|-------|---------|------|
| P0 | 登录认证 | 对接后端JWT，实现Token自动刷新 |
| P0 | 活动列表 | 分页查询、搜索筛选、状态显示 |
| P0 | 活动创建/编辑 | 表单提交、图片上传、编辑回填 |
| P0 | 活动删除 | 软删除确认、列表刷新 |
| P1 | 活动详情 | 参与者列表查看 |
| P1 | 提交审批 | 活动提交审核流程 |

**技术约束**：
- 保持与后端API `/api/v1/*` 版本对齐
- 社团端使用 axios 替代 uni.request
- 登录状态持久化到 localStorage

---

## 2. 架构设计

### 2.1 API Client 适配

由于 `shared/api/client.ts` 使用 `uni.request`，社团端需要独立的 axios 封装：

```
campus-frontend/
├── packages/
│   ├── shared/
│   │   ├── api/
│   │   │   ├── client.ts          # uni.request（小程序用）
│   │   │   ├── client.axios.ts    # 新增：axios封装（PC端用）
│   │   │   ├── endpoints.ts       # API端点（已存在）
│   │   │   └── types/             # 类型定义（已存在）
│   │   └── index.ts               # 导出区分环境
```

### 2.2 client.axios.ts 核心逻辑

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
      return Promise.reject(new Error(data.message || '请求失败'));
    }
    return data.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/club/login';
    }
    return Promise.reject(error);
  }
);

export const apiClient = {
  get: <T>(url: string, config?: any) => axiosClient.get<T>(url, config),
  post: <T>(url: string, data?: any, config?: any) => axiosClient.post<T>(url, data, config),
  put: <T>(url: string, data?: any, config?: any) => axiosClient.put<T>(url, data, config),
  delete: <T>(url: string, config?: any) => axiosClient.delete<T>(url, config),
};
```

---

## 3. 模块详细设计

### 3.1 登录认证模块

#### Store改造 (club/src/stores/user.ts)

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { Endpoints } from '@campus/shared';
import type { User, UserRole, LoginResponse } from '@campus/shared';

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>(localStorage.getItem('access_token') || '');
  const refreshToken = ref<string>(localStorage.getItem('refresh_token') || '');
  const userInfo = ref<User | null>(null);
  const loading = ref(false);

  // Getters
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value);
  const isClubAdmin = computed(() => userInfo.value?.role === UserRole.CLUB_PRESIDENT);
  const isAdmin = computed(() => 
    userInfo.value?.role === UserRole.ADMIN || userInfo.value?.role === UserRole.SUPER_ADMIN
  );

  // Actions
  const login = async (credentials: { username: string; password: string }) => {
    loading.value = true;
    try {
      const { data } = await axios.post<LoginResponse>(Endpoints.auth.wxLogin, credentials);
      token.value = data.accessToken;
      refreshToken.value = data.refreshToken;
      userInfo.value = data.user;
      localStorage.setItem('access_token', data.accessToken);
      localStorage.setItem('refresh_token', data.refreshToken);
      return true;
    } catch (error) {
      console.error('登录失败:', error);
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
        refreshToken: refreshToken.value
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
    // 从token解析或调用用户信息API
  };

  return {
    token,
    refreshToken,
    userInfo,
    loading,
    isLoggedIn,
    isClubAdmin,
    isAdmin,
    login,
    logout,
    refreshAccessToken,
    fetchUserInfo,
  };
});
```

#### 路由守卫增强 (club/src/router/index.ts)

```typescript
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login');
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/');
  } else {
    // Token即将过期时自动刷新
    if (userStore.isLoggedIn && isTokenExpiringSoon()) {
      await userStore.refreshAccessToken();
    }
    next();
  }
});
```

---

### 3.2 活动管理模块

#### API封装 (club/src/api/activity.ts)

```typescript
import { apiClient } from '@campus/shared/axios';
import { Endpoints } from '@campus/shared';
import type {
  Activity,
  ActivityCreateRequest,
  ActivityListParams,
  ActivityParticipantDto,
} from '@campus/shared';

export interface ActivityListResponse {
  items: Activity[];
  total: number;
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
    apiClient.post<void>(`${Endpoints.activities.detail(id)}/submit`),

  // 获取参与者列表
  getParticipants: (id: number) =>
    apiClient.get<ActivityParticipantDto[]>(Endpoints.activities.list + `/${id}/participants`),
};
```

#### 活动列表页改造 (club/src/views/activity/list.vue)

**API对接变更**：
- 移除模拟数据
- 使用 activityApi.getList 获取真实数据
- 实现搜索、筛选、分页参数传递
- 删除功能调用 activityApi.delete

#### 活动申请表单改造 (club/src/views/activity/apply.vue)

**API对接变更**：
- 使用 activityApi.create 创建活动
- 使用 activityApi.update 更新活动
- 编辑模式时调用 activityApi.getById 回填数据
- 提交成功后跳转列表页

#### 活动详情页完善 (club/src/views/activity/detail.vue)

**功能**：
- 使用 activityApi.getById 获取活动详情
- 使用 activityApi.getParticipants 获取参与者列表
- 使用 activityApi.submitForApproval 提交审批
- 显示参与者签到状态

---

### 3.3 类型与常量

复用 `shared` 包已定义的类型：
- `Activity`, `ActivityCreateRequest`, `ActivityStatus`, `ActivityType`
- `ApiResponse<T>`, `User`, `LoginResponse`

#### 后端API状态码映射

| 后端状态 | 前端显示 | Tag类型 |
|---------|---------|---------|
| PLANNING | 策划中 | info |
| PENDING_APPROVAL | 待审核 | warning |
| APPROVED | 已通过 | success |
| REGISTERING | 报名中 | success |
| ONGOING | 进行中 | primary |
| COMPLETED | 已结束 | info |
| REJECTED | 已拒绝 | danger |
| CANCELLED | 已取消 | danger |

---

## 4. 错误处理策略

| 场景 | 处理方式 |
|-----|---------|
| 401 Unauthorized | 清除token，跳转登录页，提示"登录已过期" |
| 403 Forbidden | Toast提示"无权限执行此操作" |
| 500 Server Error | Toast提示"服务器繁忙，请稍后重试" |
| 网络错误 | Toast提示"网络连接失败，请检查网络" |
| 业务错误 | 直接显示后端返回的 message |

---

## 5. 开发顺序与工期

```
Phase 1: 登录认证（1天）
├── 创建 client.axios.ts
├── 改造 user store（真实API对接）
├── 路由守卫Token刷新
└── 登录页面联调

Phase 2: 活动列表（1天）
├── activityApi.getList 对接
├── 分页/搜索/筛选实现
└── 删除功能对接

Phase 3: 活动创建/编辑（1天）
├── activityApi.create/update 对接
├── 编辑模式数据回填
└── 表单验证优化

Phase 4: 活动详情（0.5天）
├── activityApi.getById 对接
├── 参与者列表显示
└── 提交审批功能

Phase 5: 联调测试（0.5天）
├── 完整流程测试
├── 错误场景测试
└── Token刷新测试
```

**预计总工期**：4天

---

## 6. 关键文件变更清单

| 文件 | 操作 | 说明 |
|-----|------|------|
| `packages/shared/src/api/client.axios.ts` | 新增 | axios客户端封装 |
| `packages/shared/src/api/index.ts` | 修改 | 根据环境导出不同client |
| `packages/shared/src/index.ts` | 修改 | 导出axios client |
| `packages/shared/src/api/types/user.ts` | 修改 | 添加LoginResponse类型 |
| `packages/club/src/stores/user.ts` | 修改 | 真实登录API对接 |
| `packages/club/src/api/activity.ts` | 新增 | 活动API模块 |
| `packages/club/src/views/activity/list.vue` | 修改 | 对接真实API |
| `packages/club/src/views/activity/apply.vue` | 修改 | 对接真实API |
| `packages/club/src/views/activity/detail.vue` | 修改 | 完善详情页 |
| `packages/club/.env.development` | 新增 | API基地址配置 |
| `packages/club/.env.production` | 新增 | 生产环境配置 |

---

## 7. 后端API依赖

对接以下后端接口：

| 接口 | 方法 | 用途 |
|-----|------|------|
| `/api/v1/auth/wechat-login` | POST | 登录获取Token |
| `/api/v1/auth/refresh` | POST | 刷新Token |
| `/api/v1/activities` | GET | 活动列表（分页） |
| `/api/v1/activities` | POST | 创建活动 |
| `/api/v1/activities/{id}` | GET | 活动详情 |
| `/api/v1/activities/{id}` | PUT | 更新活动 |
| `/api/v1/activities/{id}` | DELETE | 删除活动 |
| `/api/v1/activities/{id}/submit` | POST | 提交审批 |
| `/api/v1/activities/{id}/participants` | GET | 参与者列表 |

---

## 8. 测试验收标准

- [ ] 登录成功获取Token并存储到localStorage
- [ ] Token过期前自动刷新
- [ ] Token过期后自动跳转登录页
- [ ] 活动列表正确显示分页数据
- [ ] 搜索和筛选功能正常
- [ ] 创建活动成功后出现在列表中
- [ ] 编辑活动数据正确回填
- [ ] 删除活动后列表自动刷新
- [ ] 活动详情页显示完整信息
- [ ] 参与者列表正确显示
- [ ] 提交审批功能正常
- [ ] 所有API错误正确处理并提示用户

---

**文档版本**: 1.0  
**最后更新**: 2026-04-14  
**状态**: 待实现
