# 校园社团活动评估系统 - 前端架构设计文档

## 项目概述

### 1.1 项目名称
基于大数据分析的校园社团活动效果评估与资源优化配置系统 - 前端架构设计

### 1.2 架构目标
构建支持"PC端 + 微信小程序"双端运行的前端架构，实现学生端、社团端、管理端三角色的完整业务闭环。

### 1.3 核心约束
- **人员约束**：前端开发由单人（杨壮同学）负责，工具链复杂度需可控
- **周期约束**：2025年3月 - 2027年3月（两年维护周期）
- **部署约束**：高校服务器/Nginx静态托管，CI/CD资源有限
- **需求约束**：必须支持真正的微信小程序（非H5），需调用相机等原生能力

---

## 技术栈选型

### 2.1 架构模式
采用 **Monorepo分包架构**（pnpm workspace），在代码复用与端侧隔离之间取得平衡。

### 2.2 包结构

| 包名 | 技术栈 | 目标平台 | UI组件库 |
|------|--------|----------|----------|
| `@campus/shared` | TypeScript 5.3 | 全端共享 | 无UI依赖 |
| `@campus/student` | uni-app + Vue 3.4 | 微信小程序 | Vant 4 |
| `@campus/club` | Vue 3.4 + Vite 5 | PC浏览器 | Element Plus 2.5 |
| `@campus/admin` | Vue 3.4 + Vite 5 | PC浏览器（大屏） | Element Plus 2.5 + ECharts 5 |

### 2.3 核心依赖版本

```json
{
  "vue": "^3.4.15",
  "vue-router": "^4.2.5",
  "pinia": "^2.1.7",
  "axios": "^1.6.5",
  "echarts": "^5.4.3",
  "vue-echarts": "^6.6.8",
  "element-plus": "^2.5.1",
  "vant": "^4.8.2",
  "@dcloudio/uni-app": "^3.0.0",
  "typescript": "~5.3.0"
}
```

---

## 目录结构设计

```
campus-club-frontend/
├── package.json                    # Root配置，定义workspace
├── pnpm-workspace.yaml             # pnpm工作区配置
├── turbo.json                      # Turborepo缓存配置（简化版）
├── README.md                       # 项目说明
│
├── packages/
│   │
│   ├── shared/                     # 共享包（零UI依赖）
│   │   ├── src/
│   │   │   ├── api/                # API客户端与类型定义
│   │   │   │   ├── client.ts       # Axios封装
│   │   │   │   ├── types/          # 后端API TypeScript类型
│   │   │   │   │   ├── activity.ts
│   │   │   │   │   ├── user.ts
│   │   │   │   │   ├── club.ts
│   │   │   │   │   ├── resource.ts
│   │   │   │   │   ├── evaluation.ts
│   │   │   │   │   └── index.ts
│   │   │   │   └── endpoints.ts    # API端点常量
│   │   │   │
│   │   │   ├── constants/          # 业务常量与枚举
│   │   │   │   ├── activity.ts     # 活动状态、类型枚举
│   │   │   │   ├── resource.ts     # 资源类型枚举
│   │   │   │   ├── roles.ts        # 用户角色枚举
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── utils/              # 纯工具函数
│   │   │   │   ├── format.ts       # 时间、数字格式化
│   │   │   │   ├── validators.ts   # 表单验证规则
│   │   │   │   ├── dataProcess.ts  # 大数据量处理
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   └── index.ts            # 统一导出
│   │   │
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── student/                    # 学生端（uni-app）
│   │   ├── src/
│   │   │   ├── pages/              # 页面目录
│   │   │   │   ├── index/          # 首页-活动推荐流
│   │   │   │   ├── activity/       # 活动详情页
│   │   │   │   │   ├── detail.vue
│   │   │   │   │   └── list.vue
│   │   │   │   ├── participate/    # 参与记录页
│   │   │   │   │   └── history.vue
│   │   │   │   ├── evaluate/       # 评价反馈页
│   │   │   │   │   ├── form.vue
│   │   │   │   │   └── photos.vue
│   │   │   │   └── profile/        # 个人中心页
│   │   │   │       └── index.vue
│   │   │   │
│   │   │   ├── components/         # 端侧专用组件
│   │   │   │   ├── ActivityCard.vue
│   │   │   │   ├── RatingStars.vue
│   │   │   │   └── PhotoUploader.vue
│   │   │   │
│   │   │   ├── composables/        # 组合式函数
│   │   │   │   ├── useActivities.ts
│   │   │   │   ├── useWechatAuth.ts
│   │   │   │   └── useLocation.ts
│   │   │   │
│   │   │   ├── static/             # 静态资源
│   │   │   ├── manifest.json       # 小程序配置
│   │   │   ├── pages.json          # 页面路由配置
│   │   │   ├── App.vue
│   │   │   └── main.ts
│   │   │
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── vite.config.ts
│   │
│   ├── club/                       # 社团端（Vue3 + Element Plus）
│   │   ├── src/
│   │   │   ├── views/              # 页面目录
│   │   │   │   ├── dashboard/      # 概览页
│   │   │   │   │   └── index.vue
│   │   │   │   ├── activity/       # 活动申报
│   │   │   │   │   ├── apply.vue
│   │   │   │   │   ├── list.vue
│   │   │   │   │   └── detail.vue
│   │   │   │   ├── resource/       # 资源预约
│   │   │   │   │   ├── calendar.vue
│   │   │   │   │   ├── apply.vue
│   │   │   │   │   └── status.vue
│   │   │   │   └── report/         # 效果分析报告
│   │   │   │       ├── radar.vue
│   │   │   │       └── feedback.vue
│   │   │   │
│   │   │   ├── components/         # 端侧专用组件
│   │   │   │   ├── ResourceCalendar.vue
│   │   │   │   ├── ActivityForm.vue
│   │   │   │   └── RadarChart.vue
│   │   │   │
│   │   │   ├── router/             # 路由配置
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── stores/             # Pinia状态管理
│   │   │   │   ├── user.ts
│   │   │   │   └── activity.ts
│   │   │   │
│   │   │   ├── App.vue
│   │   │   └── main.ts
│   │   │
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── vite.config.ts
│   │   └── index.html
│   │
│   └── admin/                      # 管理端（Vue3 + Element Plus + 大屏）
│       ├── src/
│       │   ├── views/              # 页面目录
│       │   │   ├── dashboard/      # 数据监控大屏
│       │   │   │   ├── index.vue
│       │   │   │   ├── components/
│       │   │   │   │   ├── StatCards.vue
│       │   │   │   │   ├── TrendChart.vue
│       │   │   │   │   └── AlertList.vue
│       │   │   │   └── composables/
│       │   │   │       └── useRealtimeData.ts
│       │   │   │
│       │   │   ├── approval/       # 活动审批台
│       │   │   │   ├── pending.vue
│       │   │   │   └── history.vue
│       │   │   │
│       │   │   ├── resource/       # 资源池管理
│       │   │   │   ├── pool.vue
│       │   │   │   └── allocation.vue
│       │   │   │
│       │   │   ├── system/         # 系统配置
│       │   │   └── report/         # 全局报表
│       │   │
│       │   ├── components/         # 大屏专用组件
│       │   │   ├── BigScreenLayout.vue
│       │   │   ├── DataCard.vue
│       │   │   └── RealtimeChart.vue
│       │   │
│       │   ├── router/
│       │   ├── stores/
│       │   ├── App.vue
│       │   └── main.ts
│       │
│       ├── package.json
│       ├── tsconfig.json
│       ├── vite.config.ts
│       └── index.html
│
└── scripts/                        # 构建与部署脚本
    ├── build.sh                    # 统一构建脚本
    └── deploy.sh                   # 部署脚本
```

---

## 核心设计决策

### 3.1 工具链简化策略（降低学习成本）

考虑到杨壮同学单人负责开发，采用**最简可用的Monorepo工具链**：

| 工具 | 用途 | 替代方案（不使用） |
|------|------|-------------------|
| pnpm workspace | 包管理 | Turborepo（过度设计） |
| TypeScript Project References | 共享包类型 | 复杂打包工具（rollup/unbuild） |
| 原生npm scripts | 任务编排 | nx/turborepo pipeline |
| 手动版本管理 | 版本控制 | changesets（单人不需要） |

**关键配置**（根目录 `package.json`）：

```json
{
  "name": "campus-club-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev:student": "pnpm --filter @campus/student dev",
    "dev:club": "pnpm --filter @campus/club dev",
    "dev:admin": "pnpm --filter @campus/admin dev",
    "build": "pnpm -r build",
    "build:student": "pnpm --filter @campus/student build",
    "build:club": "pnpm --filter @campus/club build",
    "build:admin": "pnpm --filter @campus/admin build",
    "clean": "pnpm -r exec rm -rf dist node_modules"
  },
  "devDependencies": {
    "typescript": "~5.3.0"
  }
}
```

### 3.2 API契约与类型共享（重点）

后端已配置OpenAPI/Swagger，前端通过 `@campus/shared` 包统一管理API类型：

**类型定义示例**（`packages/shared/src/api/types/activity.ts`）：

```typescript
// 与后端ApiResponse<T>对应
export interface ApiResponse<T> {
  code: string;        // "SUCCESS" | "ERROR" | 具体错误码
  message: string;
  data: T;
}

// 活动状态枚举（与数据库约束一致）
export enum ActivityStatus {
  PLANNING = 'PLANNING',       // 策划中
  REGISTERING = 'REGISTERING', // 报名中
  ONGOING = 'ONGOING',         // 进行中
  COMPLETED = 'COMPLETED',     // 已结束
  CANCELLED = 'CANCELLED',     // 已取消
}

// 活动类型（对应后端activity_type）
export enum ActivityType {
  LECTURE = 'LECTURE',         // 讲座
  WORKSHOP = 'WORKSHOP',       // 工作坊
  COMPETITION = 'COMPETITION', // 竞赛
  SOCIAL = 'SOCIAL',           // 社交活动
  VOLUNTEER = 'VOLUNTEER',     // 志愿活动
}

// 活动实体（与数据库表activities对应）
export interface Activity {
  id: number;
  title: string;
  description: string;
  clubId: number;
  organizerId: number;
  activityType: ActivityType;
  startTime: string;           // ISO 8601格式
  endTime: string;
  location: string;
  maxParticipants: number;
  currentParticipants: number;
  status: ActivityStatus;
  coverImageUrl: string;
  createdAt: string;
  updatedAt: string;
}

// API请求/响应类型
export interface ActivityCreateRequest {
  title: string;
  description: string;
  clubId: number;
  activityType: ActivityType;
  startTime: string;
  endTime: string;
  location: string;
  maxParticipants: number;
}

export type ActivityCreateResponse = ApiResponse<Activity>;
export type ActivityListResponse = ApiResponse<Activity[]>;
export type ActivityDetailResponse = ApiResponse<Activity>;
```

**API端点常量**（`packages/shared/src/api/endpoints.ts`）：

```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const Endpoints = {
  // 活动相关
  activities: {
    list: `${API_BASE_URL}/activities`,
    detail: (id: number) => `${API_BASE_URL}/activities/${id}`,
    create: `${API_BASE_URL}/activities`,
    update: (id: number) => `${API_BASE_URL}/activities/${id}`,
    delete: (id: number) => `${API_BASE_URL}/activities/${id}`,
    join: (id: number) => `${API_BASE_URL}/activities/${id}/join`,
    evaluate: (id: number) => `${API_BASE_URL}/activities/${id}/evaluate`,
    recommend: `${API_BASE_URL}/activities/recommend`,
  },
  // 用户相关
  auth: {
    login: `${API_BASE_URL}/auth/login`,
    wxLogin: `${API_BASE_URL}/auth/wx-login`,
    refresh: `${API_BASE_URL}/auth/refresh`,
    profile: `${API_BASE_URL}/auth/profile`,
  },
  // 资源相关
  resources: {
    list: `${API_BASE_URL}/resources`,
    reserve: `${API_BASE_URL}/resources/reserve`,
    myReservations: `${API_BASE_URL}/resources/my-reservations`,
  },
  // 评估相关
  evaluation: {
    report: (activityId: number) => `${API_BASE_URL}/evaluation/${activityId}/report`,
    radar: (activityId: number) => `${API_BASE_URL}/evaluation/${activityId}/radar`,
  },
} as const;
```

### 3.3 各端差异化策略

| 维度 | student（学生端） | club（社团端） | admin（管理端） |
|------|------------------|----------------|-----------------|
| **目标终端** | 微信小程序 | PC浏览器 | PC浏览器（大屏） |
| **主要场景** | 活动发现、报名、评价 | 活动申报、资源预约 | 审批、监控、决策 |
| **UI组件库** | Vant 4（移动优先） | Element Plus | Element Plus |
| **路由模式** | 页面栈（pages.json） | History模式 | History模式 |
| **状态持久化** | 微信本地存储 | localStorage | localStorage |
| **可视化** | 简单图表 | ECharts雷达图 | ECharts + 数据大屏 |
| **特色能力** | 扫码、拍照、位置 | 文件上传、日历 | 实时数据、导出报表 |

### 3.4 组件库共存策略

在开发阶段，各端独立引入所需组件库，构建时Tree-shaking自动剔除未使用代码：

```typescript
// packages/student/src/main.ts
import { createSSRApp } from 'vue';
import { Button, Cell, Card, Image, Uploader, Toast } from 'vant';
import 'vant/lib/index.css';

export function createApp() {
  const app = createSSRApp(App);
  app.use(Button).use(Cell).use(Card).use(Image).use(Uploader).use(Toast);
  return { app };
}

// packages/club/src/main.ts
import { createApp } from 'vue';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

const app = createApp(App);
app.use(ElementPlus);
```

---

## 状态管理设计

### 4.1 全局状态分层

```
┌─────────────────────────────────────────────────────────────┐
│                     全局状态（Pinia）                        │
├─────────────────┬─────────────────┬─────────────────────────┤
│   UserStore     │  ActivityStore  │    ResourceStore        │
│  - token        │  - list         │    - pool               │
│  - profile      │  - detail       │    - reservations       │
│  - permissions  │  - recommend    │    - calendar           │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### 4.2 Store设计示例

```typescript
// packages/club/src/stores/user.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, UserRole } from '@campus/shared';

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string>('');
  const userInfo = ref<User | null>(null);
  
  // Getters
  const isLoggedIn = computed(() => !!token.value);
  const isClubAdmin = computed(() => userInfo.value?.role === UserRole.CLUB_PRESIDENT);
  const isAdmin = computed(() => userInfo.value?.role === UserRole.ADMIN);
  
  // Actions
  const login = async (credentials: { username: string; password: string }) => {
    // 调用API...
  };
  
  const logout = () => {
    token.value = '';
    userInfo.value = null;
  };
  
  return { token, userInfo, isLoggedIn, isClubAdmin, isAdmin, login, logout };
});
```

---

## 路由与权限设计

### 5.1 学生端路由（pages.json）

```json
{
  "pages": [
    { "path": "pages/index/index", "style": { "navigationBarTitleText": "活动推荐" } },
    { "path": "pages/activity/list", "style": { "navigationBarTitleText": "活动列表" } },
    { "path": "pages/activity/detail", "style": { "navigationBarTitleText": "活动详情" } },
    { "path": "pages/participate/history", "style": { "navigationBarTitleText": "参与记录" } },
    { "path": "pages/evaluate/form", "style": { "navigationBarTitleText": "评价活动" } },
    { "path": "pages/profile/index", "style": { "navigationBarTitleText": "个人中心" } }
  ],
  "tabBar": {
    "list": [
      { "pagePath": "pages/index/index", "text": "推荐" },
      { "pagePath": "pages/participate/history", "text": "记录" },
      { "pagePath": "pages/profile/index", "text": "我的" }
    ]
  }
}
```

### 5.2 PC端路由（Vue Router）

```typescript
// packages/club/src/router/index.ts
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: Layout,
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/dashboard/index.vue') },
      { path: 'activities', name: 'ActivityList', component: () => import('@/views/activity/list.vue') },
      { path: 'activities/apply', name: 'ActivityApply', component: () => import('@/views/activity/apply.vue') },
      { path: 'resources/calendar', name: 'ResourceCalendar', component: () => import('@/views/resource/calendar.vue') },
      { path: 'resources/apply', name: 'ResourceApply', component: () => import('@/views/resource/apply.vue') },
      { path: 'reports', name: 'Reports', component: () => import('@/views/report/radar.vue') },
    ],
    meta: { requiresAuth: true, role: 'CLUB' }
  },
  { path: '/login', name: 'Login', component: () => import('@/views/login/index.vue') },
];

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login');
  } else {
    next();
  }
});
```

---

## 数据可视化方案

### 6.1 五维评估雷达图（社团端/管理端共用）

```vue
<!-- packages/shared/components/RadarChart.vue -->
<template>
  <v-chart class="radar-chart" :option="option" autoresize />
</template>

<script setup lang="ts">
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { RadarChart } from 'echarts/charts';
import { TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, RadarChart, TooltipComponent, LegendComponent]);

interface RadarData {
  participation: number;
  educational: number;
  innovation: number;
  influence: number;
  sustainability: number;
}

const props = defineProps<{
  data: RadarData;
}>();

const option = computed(() => ({
  radar: {
    indicator: [
      { name: '参与度', max: 100 },
      { name: '教育性', max: 100 },
      { name: '创新性', max: 100 },
      { name: '影响力', max: 100 },
      { name: '可持续性', max: 100 },
    ],
  },
  series: [{
    type: 'radar',
    data: [{
      value: [
        props.data.participation,
        props.data.educational,
        props.data.innovation,
        props.data.influence,
        props.data.sustainability,
      ],
      name: '活动评估',
    }],
  }],
}));
</script>
```

### 6.2 管理端大屏图表

```typescript
// packages/admin/src/composables/useRealtimeData.ts
import { ref, onMounted, onUnmounted } from 'vue';

export function useRealtimeData() {
  const stats = ref({
    totalActivities: 0,
    totalParticipants: 0,
    pendingApprovals: 0,
    resourceUtilization: 0,
  });
  
  let timer: number;
  
  const fetchData = async () => {
    // 调用API获取实时数据
  };
  
  onMounted(() => {
    fetchData();
    timer = window.setInterval(fetchData, 30000); // 30秒刷新
  });
  
  onUnmounted(() => {
    clearInterval(timer);
  });
  
  return { stats };
}
```

---

## 构建与部署方案

### 7.1 开发环境启动

```bash
# 安装依赖
pnpm install

# 开发各端（并行）
pnpm dev:student    # 启动uni-app开发服务器
pnpm dev:club       # 启动社团端Vite服务器
pnpm dev:admin      # 启动管理端Vite服务器
```

### 7.2 生产构建

```bash
# 构建所有包
pnpm build

# 构建单个包
pnpm build:student
pnpm build:club
pnpm build:admin
```

### 7.3 部署结构（Nginx）

```
/usr/share/nginx/html/
├── student/                    # 小程序构建产物（上传微信开发者工具）
├── club/                       # 社团端静态文件
│   ├── index.html
│   └── assets/
└── admin/                      # 管理端静态文件
    ├── index.html
    └── assets/
```

### 7.4 Nginx配置示例

```nginx
server {
    listen 80;
    server_name campus-club.edu.cn;
    
    # 社团端
    location /club {
        alias /usr/share/nginx/html/club;
        try_files $uri $uri/ /club/index.html;
    }
    
    # 管理端
    location /admin {
        alias /usr/share/nginx/html/admin;
        try_files $uri $uri/ /admin/index.html;
    }
    
    # API代理
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 与后端对接规范

### 8.1 API响应处理

```typescript
// packages/shared/src/api/client.ts
import axios from 'axios';
import type { ApiResponse } from './types';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    const data = response.data as ApiResponse<any>;
    if (data.code !== 'SUCCESS') {
      return Promise.reject(new Error(data.message));
    }
    return data.data;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 8.2 错误处理策略

| 错误码 | 处理方式 |
|--------|----------|
| 401 Unauthorized | 跳转登录页 / 触发微信重新授权 |
| 403 Forbidden | 提示无权限，返回首页 |
| 500 Server Error | Toast提示"服务繁忙，请稍后重试" |
| Network Error | 提示网络异常，支持重试 |

---

## 实施计划

### 第一阶段：基建（1周）

1. 初始化Monorepo结构
2. 配置pnpm workspace
3. 搭建`@campus/shared`包基础类型
4. 初始化各端项目模板

### 第二阶段：学生端开发（3周）

1. 微信登录授权
2. 活动推荐列表页
3. 活动详情与报名
4. 参与记录与评价
5. 照片上传功能

### 第三阶段：社团端开发（2周）

1. 活动申报表单
2. 资源预约日历
3. 效果分析报告（雷达图）

### 第四阶段：管理端开发（2周）

1. 数据监控大屏
2. 活动审批台
3. 资源池管理
4. 智能决策展示

---

## 附录

### A.1 环境变量配置

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8080/api
VITE_APP_ENV=development

# .env.production
VITE_API_BASE_URL=/api
VITE_APP_ENV=production
```

### A.2 推荐的VS Code插件

- Vue - Official (Vue官方插件)
- TypeScript Vue Plugin (Volar)
- ESLint
- Prettier
- uni-app 插件（开发小程序时）

---

*文档版本：1.0*
*最后更新：2026-04-13*
*设计者：Claude Code*
*状态：待审核*
