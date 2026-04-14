# 校园社团活动评估系统 - 前端正式开发设计文档

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档版本 | 1.0 |
| 编写日期 | 2026-04-14 |
| 文档状态 | 正式开发版 |
| 编写者 | Claude Code |

---

## 一、项目概述

### 1.1 项目背景
基于大数据分析的校园社团活动效果评估与资源优化配置系统，需要支持"PC端 + 微信小程序"双端运行，实现学生端、社团端、管理端三角色的完整业务闭环。

### 1.2 开发目标
完成前端三端（学生端、社团端、管理端）的全部功能开发，实现与后端API的完整对接。

### 1.3 当前状态
| 模块 | 状态 | 完成度 |
|------|------|--------|
| 基础架构 | ✅ 已完成 | 100% |
| 共享类型包 | ✅ 已完成 | 100% |
| 学生端框架 | ✅ 已完成 | 80% |
| 社团端框架 | ✅ 已完成 | 70% |
| 管理端框架 | ✅ 已完成 | 70% |
| API对接 | 🔄 进行中 | 20% |

---

## 二、技术架构

### 2.1 Monorepo 架构

```
campus-frontend/
├── packages/
│   ├── shared/          # 共享包（零UI依赖）
│   ├── student/         # 学生端（uni-app 微信小程序）
│   ├── club/            # 社团端（Vue3 + Vite + Element Plus）
│   └── admin/           # 管理端（Vue3 + Vite + Element Plus + ECharts）
├── scripts/             # 构建与部署脚本
├── package.json         # 根配置
└── pnpm-workspace.yaml  # pnpm工作区配置
```

### 2.2 技术栈详情

| 包名 | 技术栈 | 目标平台 | UI组件库 |
|------|--------|----------|----------|
| `@campus/shared` | TypeScript 5.3 | 全端共享 | 无UI依赖 |
| `@campus/student` | uni-app 3.0 + Vue 3.4 | 微信小程序 | Vant 4 + uni-ui |
| `@campus/club` | Vue 3.4 + Vite 5 | PC浏览器 | Element Plus 2.5 |
| `@campus/admin` | Vue 3.4 + Vite 5 | PC浏览器（大屏） | Element Plus 2.5 + ECharts 5 |

### 2.3 核心依赖版本

```json
{
  "vue": "^3.5.32",
  "vue-router": "^4.2.5",
  "pinia": "^2.3.1",
  "axios": "^1.15.0",
  "echarts": "^5.6.0",
  "vue-echarts": "^6.7.3",
  "element-plus": "^2.9.7",
  "vant": "^4.9.17",
  "@dcloudio/uni-app": "^3.0.0",
  "typescript": "~5.3.0"
}
```

---

## 三、共享包设计 (@campus/shared)

### 3.1 目录结构

```
packages/shared/
├── src/
│   ├── api/
│   │   ├── client.ts       # 基于uni.request的API客户端
│   │   ├── endpoints.ts    # API端点常量
│   │   └── types/          # TypeScript类型定义
│   │       ├── activity.ts
│   │       ├── user.ts
│   │       ├── club.ts
│   │       ├── resource.ts
│   │       ├── evaluation.ts
│   │       └── index.ts
│   ├── constants/          # 业务常量与枚举
│   │   ├── activity.ts
│   │   ├── resource.ts
│   │   ├── roles.ts
│   │   └── index.ts
│   ├── utils/              # 纯工具函数
│   │   ├── format.ts
│   │   ├── validators.ts
│   │   ├── dataProcess.ts
│   │   └── index.ts
│   └── index.ts
├── package.json
└── tsconfig.json
```

### 3.2 核心类型定义

#### 用户相关 (user.ts)
- `UserRole` - 用户角色枚举（STUDENT, CLUB_MEMBER, CLUB_PRESIDENT, ADMIN, SUPER_ADMIN）
- `User` - 用户实体
- `LoginRequest/LoginResponse` - 登录请求/响应
- `UserParticipationStats` - 用户参与统计

#### 活动相关 (activity.ts)
- `ActivityStatus` - 活动状态枚举（策划中、待审批、已批准、报名中、进行中、已结束等）
- `ActivityType` - 活动类型枚举（讲座、工作坊、竞赛等）
- `Activity` - 活动实体
- `ActivityCreateRequest/UpdateRequest` - 活动创建/更新请求
- `ActivityEvaluateRequest` - 活动评价请求
- `ActivityEvaluationDimensions` - 五维评估数据
- `ActivityEvaluationReport` - 活动评估报告

#### 资源相关 (resource.ts)
- `ResourceType` - 资源类型枚举
- `Resource` - 资源实体
- `ResourceReservation` - 资源预约

### 3.3 API客户端

基于 `uni.request` 实现，兼容uni-app所有平台（微信小程序、H5等）：

```typescript
// 创建API客户端
const apiClient = createApiClient({
  baseURL: '/api',
  timeout: 30000
});

// 使用方法
const activities = await apiClient.get<Activity[]>('/activities');
const newActivity = await apiClient.post<Activity>('/activities', data);
```

### 3.4 工具函数

- `formatDateTime` - 日期时间格式化
- `formatRelativeTime` - 相对时间格式化（刚刚、X分钟前等）
- `formatNumber` - 数字千分位格式化
- `formatFileSize` - 文件大小格式化
- `formatDuration` - 时长格式化
- `hasPermission` - 权限检查

---

## 四、学生端开发 (student)

### 4.1 技术栈

- **框架**: uni-app 3.0 (Vue 3 Composition API)
- **UI库**: Vant 4 + uni-ui
- **状态管理**: Pinia
- **构建工具**: Vite

### 4.2 页面结构

```
src/
├── pages/
│   ├── index/index.vue         # 首页-活动推荐流 ⭐
│   ├── activity/
│   │   ├── list.vue            # 活动列表页
│   │   └── detail.vue          # 活动详情页 ⭐
│   ├── participate/
│   │   └── history.vue         # 参与记录页 ⭐
│   ├── evaluate/
│   │   ├── form.vue            # 评价表单页 ⭐
│   │   └── photos.vue          # 照片上传页
│   └── profile/
│       └── index.vue           # 个人中心页 ⭐
├── components/
│   ├── ActivityCard.vue        # 活动卡片组件
│   ├── RatingStars.vue         # 星级评分组件 ✅
│   └── PhotoUploader.vue       # 照片上传组件 ✅
├── composables/
│   ├── useActivities.ts        # 活动相关组合式函数
│   ├── useWechatAuth.ts        # 微信授权组合式函数
│   └── useLocation.ts          # 地理位置组合式函数
├── static/                     # 静态资源
├── manifest.json               # 小程序配置 ✅
├── pages.json                  # 页面路由配置 ✅
├── App.vue                     # 应用根组件 ✅
└── main.ts                     # 入口文件 ✅
```

### 4.3 核心功能模块

| 模块 | 功能描述 | 优先级 | 状态 |
|------|----------|--------|------|
| 微信登录 | 微信授权登录，获取用户信息 | P0 | 🔄 待对接 |
| 活动推荐 | 基于AI算法的活动推荐流 | P0 | 🔄 待开发 |
| 活动详情 | 活动信息展示、报名按钮 | P0 | 🔄 待开发 |
| 活动报名 | 一键报名、取消报名 | P0 | 🔄 待开发 |
| 评价反馈 | 五星评分+文字评价+照片上传 | P0 | 🔄 待开发 |
| 参与记录 | 历史参与活动列表 | P1 | 🔄 待开发 |
| 个人中心 | 用户信息、设置 | P1 | 🔄 待开发 |

### 4.4 页面配置 (pages.json)

```json
{
  "pages": [
    { "path": "pages/index/index", "style": { "navigationBarTitleText": "活动推荐", "navigationStyle": "custom" }},
    { "path": "pages/activity/list", "style": { "navigationBarTitleText": "活动列表" }},
    { "path": "pages/activity/detail", "style": { "navigationBarTitleText": "活动详情" }},
    { "path": "pages/participate/history", "style": { "navigationBarTitleText": "参与记录" }},
    { "path": "pages/evaluate/form", "style": { "navigationBarTitleText": "评价活动" }},
    { "path": "pages/evaluate/photos", "style": { "navigationBarTitleText": "上传照片" }},
    { "path": "pages/profile/index", "style": { "navigationBarTitleText": "个人中心", "navigationStyle": "custom" }}
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

---

## 五、社团端开发 (club)

### 5.1 技术栈

- **框架**: Vue 3.4 + Composition API
- **UI库**: Element Plus 2.5
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **图表**: ECharts 5 + vue-echarts
- **构建工具**: Vite 5

### 5.2 页面结构

```
src/
├── views/
│   ├── login/
│   │   └── index.vue           # 登录页 ✅
│   ├── dashboard/
│   │   └── index.vue           # 概览页 ✅（需对接API）
│   ├── activity/
│   │   ├── list.vue            # 活动列表页 ⭐
│   │   ├── apply.vue           # 活动申报页 ⭐
│   │   └── detail.vue          # 活动详情页 ⭐
│   ├── resource/
│   │   ├── calendar.vue        # 资源日历页 ⭐
│   │   ├── apply.vue           # 资源预约页
│   │   └── status.vue          # 预约状态页
│   └── report/
│       ├── radar.vue           # 效果分析页（雷达图）⭐
│       └── feedback.vue        # 反馈汇总页
├── components/
│   ├── ResourceCalendar.vue    # 资源日历组件
│   ├── ActivityForm.vue        # 活动表单组件
│   └── RadarChart.vue          # 雷达图组件
├── router/
│   └── index.ts                # 路由配置 ✅
├── stores/
│   ├── user.ts                 # 用户状态管理 ✅
│   └── activity.ts             # 活动状态管理
├── layouts/
│   └── MainLayout.vue          # 主布局组件 ✅
├── App.vue                     # 应用根组件 ✅
└── main.ts                     # 入口文件 ✅
```

### 5.3 路由配置

```typescript
const routes = [
  { path: '/login', component: () => import('@/views/login/index.vue'), meta: { public: true }},
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/dashboard/index.vue') },
      { path: 'activities', name: 'ActivityList', component: () => import('@/views/activity/list.vue') },
      { path: 'activities/apply', name: 'ActivityApply', component: () => import('@/views/activity/apply.vue') },
      { path: 'activities/:id', name: 'ActivityDetail', component: () => import('@/views/activity/detail.vue') },
      { path: 'resources/calendar', name: 'ResourceCalendar', component: () => import('@/views/resource/calendar.vue') },
      { path: 'resources/apply', name: 'ResourceApply', component: () => import('@/views/resource/apply.vue') },
      { path: 'resources/status', name: 'ResourceStatus', component: () => import('@/views/resource/status.vue') },
      { path: 'reports/radar', name: 'ReportRadar', component: () => import('@/views/report/radar.vue') },
      { path: 'reports/feedback', name: 'ReportFeedback', component: () => import('@/views/report/feedback.vue') },
    ]
  }
];
```

### 5.4 核心功能模块

| 模块 | 功能描述 | 优先级 | 状态 |
|------|----------|--------|------|
| 账号登录 | 用户名密码登录 | P0 | ✅ 框架完成 |
| 数据概览 | 统计卡片、活动趋势图表 | P0 | 🔄 待对接API |
| 活动申报 | 表单提交活动信息 | P0 | 🔄 待开发 |
| 活动管理 | 列表展示、编辑、取消 | P0 | 🔄 待开发 |
| 资源预约 | 日历选择、时段预约 | P0 | 🔄 待开发 |
| 效果分析 | 五维雷达图展示 | P1 | 🔄 待开发 |
| 反馈汇总 | 学生评价列表 | P1 | 🔄 待开发 |

---

## 六、管理端开发 (admin)

### 6.1 技术栈

- **框架**: Vue 3.4 + Composition API
- **UI库**: Element Plus 2.5
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **图表**: ECharts 5 + vue-echarts
- **构建工具**: Vite 5

### 6.2 页面结构

```
src/
├── views/
│   ├── login/
│   │   └── index.vue           # 登录页 ✅
│   ├── dashboard/
│   │   └── index.vue           # 数据监控大屏 ✅（需对接API）
│   ├── approval/
│   │   ├── pending.vue         # 待办审批页 ⭐
│   │   └── history.vue         # 审批历史页
│   ├── resource/
│   │   ├── pool.vue            # 资源池管理页 ⭐
│   │   └── allocation.vue      # 资源分配页
│   ├── report/
│   │   └── index.vue           # 全局报表页
│   └── system/
│       └── config.vue          # 系统配置页
├── components/
│   ├── BigScreenLayout.vue     # 大屏布局组件
│   ├── DataCard.vue            # 数据卡片组件
│   └── RealtimeChart.vue       # 实时图表组件
├── router/
│   └── index.ts                # 路由配置 ✅
├── stores/
│   └── user.ts                 # 用户状态管理 ✅
├── layouts/
│   └── MainLayout.vue          # 主布局组件 ✅
├── App.vue                     # 应用根组件 ✅
└── main.ts                     # 入口文件 ✅
```

### 6.3 路由配置

```typescript
const routes = [
  { path: '/login', component: () => import('@/views/login/index.vue'), meta: { public: true }},
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/dashboard/index.vue') },
      { path: 'approval/pending', name: 'ApprovalPending', component: () => import('@/views/approval/pending.vue') },
      { path: 'approval/history', name: 'ApprovalHistory', component: () => import('@/views/approval/history.vue') },
      { path: 'resource/pool', name: 'ResourcePool', component: () => import('@/views/resource/pool.vue') },
      { path: 'resource/allocation', name: 'ResourceAllocation', component: () => import('@/views/resource/allocation.vue') },
      { path: 'report/global', name: 'GlobalReport', component: () => import('@/views/report/index.vue') },
      { path: 'system/config', name: 'SystemConfig', component: () => import('@/views/system/config.vue') },
    ]
  }
];
```

### 6.4 核心功能模块

| 模块 | 功能描述 | 优先级 | 状态 |
|------|----------|--------|------|
| 管理员登录 | 账号密码登录 | P0 | ✅ 框架完成 |
| 数据大屏 | 实时统计数据、趋势图表 | P0 | 🔄 待对接API |
| 活动审批 | 待审批列表、审批操作 | P0 | 🔄 待开发 |
| 资源管理 | 资源池CRUD、使用统计 | P0 | 🔄 待开发 |
| 资源分配 | 智能分配算法结果展示 | P1 | 🔄 待开发 |
| 全局报表 | 多维度数据报表 | P1 | 🔄 待开发 |
| 系统配置 | 参数配置、权限管理 | P2 | 🔄 待开发 |

---

## 七、开发计划

### 7.1 第一阶段：API对接与基础功能（第1-2周）

**目标**: 完成三端与后端API的对接，实现基础功能

| 任务 | 描述 | 预计工时 |
|------|------|----------|
| API客户端完善 | 完善请求拦截、错误处理、token刷新 | 4h |
| 学生端微信登录 | 对接微信登录API，获取用户信息 | 6h |
| 学生端首页开发 | 活动推荐列表、下拉刷新、上拉加载 | 8h |
| 活动详情页开发 | 活动信息展示、报名功能 | 6h |
| 社团端登录对接 | 对接后端登录API | 4h |
| 管理端登录对接 | 对接后端登录API | 4h |
| 活动列表页 | 分页列表、筛选功能 | 6h |

### 7.2 第二阶段：核心业务功能（第3-4周）

**目标**: 完成核心业务功能开发

| 任务 | 描述 | 预计工时 |
|------|------|----------|
| 活动申报 | 表单验证、图片上传、提交 | 8h |
| 资源预约 | 日历组件、时段选择、冲突检测 | 10h |
| 活动审批 | 审批列表、通过/驳回操作 | 6h |
| 评价反馈 | 星级评分、文字评价、照片上传 | 8h |
| 参与记录 | 历史记录列表、状态展示 | 4h |
| 个人中心 | 用户信息、我的活动、设置 | 6h |

### 7.3 第三阶段：数据可视化（第5周）

**目标**: 完成图表和数据展示功能

| 任务 | 描述 | 预计工时 |
|------|------|----------|
| 雷达图组件 | 五维评估雷达图 | 6h |
| 数据大屏 | 实时数据展示、趋势图表 | 10h |
| 统计报表 | 数据筛选、导出功能 | 8h |
| 效果分析页 | 社团端活动效果分析 | 6h |

### 7.4 第四阶段：优化与联调（第6周）

**目标**: 完善细节，进行全面联调测试

| 任务 | 描述 | 预计工时 |
|------|------|----------|
| 性能优化 | 图片懒加载、代码分割 | 6h |
| 错误处理 | 全局错误提示、重试机制 | 4h |
| 联调测试 | 与后端联调、Bug修复 | 10h |
| 文档完善 | 使用说明、部署文档 | 4h |

---

## 八、API对接规范

### 8.1 后端API地址

- 开发环境: `http://localhost:8080/api`
- API文档: `http://localhost:8080/docs` (Swagger UI)

### 8.2 认证方式

- PC端（社团/管理）: JWT Token，存储于 localStorage
- 小程序端（学生）: 微信登录code换取token，存储于 uni.getStorage

### 8.3 请求/响应格式

```typescript
// 统一响应格式
interface ApiResponse<T> {
  code: string;      // "SUCCESS" | "ERROR" | 具体错误码
  message: string;   // 提示信息
  data: T;           // 实际数据
}

// 分页响应
interface PageResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}
```

### 8.4 错误处理

| 错误码 | 状态 | 处理方式 |
|--------|------|----------|
| 401 | Unauthorized | 跳转登录页 / 触发重新授权 |
| 403 | Forbidden | 提示无权限，返回首页 |
| 404 | Not Found | Toast提示"资源不存在" |
| 422 | Validation Error | 表单错误提示 |
| 500 | Server Error | Toast提示"服务繁忙，请稍后重试" |

---

## 九、开发规范

### 9.1 代码风格

- 使用 TypeScript 进行类型检查
- 遵循 Vue 3 Composition API 风格
- 组件名使用 PascalCase
- 组合式函数使用 useXxx 命名
- 类型定义使用接口（interface）优先

### 9.2 文件命名

- 组件文件: PascalCase (如 `ActivityCard.vue`)
- 页面文件: camelCase (如 `activityList.vue`)
- 工具函数: camelCase (如 `formatDate.ts`)
- 类型定义: 与业务模块同名 (如 `activity.ts`)

### 9.3 Git提交规范

```
feat: 新功能
fix: 修复
docs: 文档
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

---

## 十、部署方案

### 10.1 构建命令

```bash
# 安装依赖
pnpm install

# 开发模式
pnpm dev:student    # 学生端（微信小程序）
pnpm dev:club       # 社团端
pnpm dev:admin      # 管理端

# 生产构建
pnpm build:student  # 构建学生端（生成dist/build/mp-weixin）
pnpm build:club     # 构建社团端（生成dist/club）
pnpm build:admin    # 构建管理端（生成dist/admin）
```

### 10.2 部署结构（Nginx）

```
/usr/share/nginx/html/
├── club/                       # 社团端静态文件
│   ├── index.html
│   └── assets/
└── admin/                      # 管理端静态文件
    ├── index.html
    └── assets/
```

### 10.3 Nginx配置

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

## 十一、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 微信小程序审核 | 中 | 提前准备审核材料，预留审核时间 |
| API联调问题 | 高 | 使用Mock数据并行开发，定期联调 |
| 性能问题 | 中 | 使用懒加载、分页、缓存优化 |
| 浏览器兼容性 | 低 | 使用现代浏览器特性检测，提供降级方案 |

---

## 十二、附录

### 12.1 环境变量配置

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8080/api
VITE_APP_ENV=development

# .env.production
VITE_API_BASE_URL=/api
VITE_APP_ENV=production
```

### 12.2 推荐VS Code插件

- Vue - Official (Vue官方插件)
- TypeScript Vue Plugin (Volar)
- ESLint
- Prettier
- uni-app 插件（开发小程序时）

### 12.3 相关文档

- [前端架构设计文档](./2026-04-13-frontend-architecture-design.md)
- [后端API文档](http://localhost:8080/docs)
- [uni-app文档](https://uniapp.dcloud.net.cn/)
- [Element Plus文档](https://element-plus.org/)

---

*文档版本：1.0*
*最后更新：2026-04-14*
*状态：正式开发版*
