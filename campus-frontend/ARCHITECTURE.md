# 校园社团活动评估系统 - 前端架构概览

## 项目结构

```
campus-frontend/
├── package.json                    # 根配置，定义 workspace
├── pnpm-workspace.yaml             # pnpm 工作区配置
├── README.md                       # 项目说明
├── ARCHITECTURE.md                 # 架构文档（本文档）
│
├── packages/
│   ├── shared/                     # 共享包（零 UI 依赖）
│   │   ├── src/
│   │   │   ├── api/                # API 客户端与类型定义
│   │   │   │   ├── client.ts       # Axios 封装
│   │   │   │   ├── endpoints.ts    # API 端点常量
│   │   │   │   └── types/          # TypeScript 类型定义
│   │   │   │       ├── activity.ts
│   │   │   │       ├── user.ts
│   │   │   │       ├── club.ts
│   │   │   │       ├── resource.ts
│   │   │   │       ├── evaluation.ts
│   │   │   │       └── index.ts
│   │   │   ├── constants/          # 业务常量与枚举
│   │   │   │   ├── activity.ts
│   │   │   │   ├── resource.ts
│   │   │   │   ├── roles.ts
│   │   │   │   └── index.ts
│   │   │   ├── utils/              # 纯工具函数
│   │   │   │   ├── format.ts       # 时间、数字格式化
│   │   │   │   ├── validators.ts   # 表单验证规则
│   │   │   │   ├── dataProcess.ts  # 大数据量处理
│   │   │   │   └── index.ts
│   │   │   └── index.ts            # 统一导出
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── student/                    # 学生端（uni-app 微信小程序）
│   │   ├── src/
│   │   │   ├── pages/              # 页面目录
│   │   │   │   ├── index/          # 首页-活动推荐流
│   │   │   │   │   └── index.vue
│   │   │   │   ├── activity/       # 活动详情页
│   │   │   │   │   └── detail.vue
│   │   │   │   ├── participate/    # 参与记录页
│   │   │   │   ├── evaluate/       # 评价反馈页
│   │   │   │   └── profile/        # 个人中心页
│   │   │   ├── components/         # 端侧专用组件
│   │   │   │   ├── ActivityCard.vue
│   │   │   │   ├── RatingStars.vue
│   │   │   │   └── PhotoUploader.vue
│   │   │   ├── manifest.json       # 小程序配置
│   │   │   ├── pages.json          # 页面路由配置
│   │   │   ├── App.vue
│   │   │   └── main.ts
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── vite.config.ts
│   │
│   ├── club/                       # 社团端（Vue3 + Element Plus）
│   │   ├── src/
│   │   │   ├── views/              # 页面目录
│   │   │   │   ├── dashboard/      # 概览页
│   │   │   │   │   └── index.vue
│   │   │   │   ├── activity/       # 活动管理
│   │   │   │   │   ├── list.vue
│   │   │   │   │   ├── apply.vue
│   │   │   │   │   └── detail.vue
│   │   │   │   ├── resource/       # 资源预约
│   │   │   │   │   ├── calendar.vue
│   │   │   │   │   └── apply.vue
│   │   │   │   └── report/         # 效果分析报告
│   │   │   ├── components/         # 端侧专用组件
│   │   │   ├── router/             # 路由配置
│   │   │   ├── stores/             # Pinia 状态管理
│   │   │   ├── layouts/            # 布局组件
│   │   │   ├── App.vue
│   │   │   └── main.ts
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── vite.config.ts
│   │   └── index.html
│   │
│   └── admin/                      # 管理端（Vue3 + Element Plus + 大屏）
│       ├── src/
│       │   ├── views/              # 页面目录
│       │   │   ├── dashboard/      # 数据监控大屏
│       │   │   │   └── index.vue
│       │   │   ├── approval/       # 活动审批台
│       │   │   ├── resource/       # 资源池管理
│       │   │   └── report/         # 全局报表
│       │   ├── components/         # 大屏专用组件
│       │   ├── router/
│       │   ├── stores/
│       │   ├── layouts/
│       │   ├── App.vue
│       │   └── main.ts
│       ├── package.json
│       ├── tsconfig.json
│       ├── vite.config.ts
│       └── index.html
│
└── scripts/                        # 构建与部署脚本
    ├── build.sh                    # 统一构建脚本
    └── deploy.sh                   # 部署脚本
```

## 技术栈

| 包名 | 技术栈 | 目标平台 | UI 组件库 |
|------|--------|----------|-----------|
| `@campus/shared` | TypeScript 5.3 | 全端共享 | 无 UI 依赖 |
| `@campus/student` | uni-app + Vue 3.4 | 微信小程序 | Vant 4 |
| `@campus/club` | Vue 3.4 + Vite 5 | PC 浏览器 | Element Plus 2.5 |
| `@campus/admin` | Vue 3.4 + Vite 5 | PC 浏览器（大屏） | Element Plus 2.5 + ECharts 5 |

## 核心依赖版本

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
  "typescript": "~5.3.0"
}
```

## 快速开始

### 环境要求

- Node.js >= 18.0.0
- pnpm >= 8.0.0

### 安装依赖

```bash
F:/nodejs/pnpm install
```

### 开发模式

```bash
# 启动学生端（微信小程序）
F:/nodejs/pnpm dev:student

# 启动社团端
F:/nodejs/pnpm dev:club

# 启动管理端
F:/nodejs/pnpm dev:admin
```

### 生产构建

```bash
# 构建所有包
F:/nodejs/pnpm build

# 或运行构建脚本
cd scripts && ./build.sh
```

## 各端差异化策略

| 维度 | student（学生端） | club（社团端） | admin（管理端） |
|------|------------------|----------------|-----------------|
| **目标终端** | 微信小程序 | PC 浏览器 | PC 浏览器（大屏） |
| **主要场景** | 活动发现、报名、评价 | 活动申报、资源预约 | 审批、监控、决策 |
| **UI 组件库** | Vant 4（移动优先） | Element Plus | Element Plus |
| **路由模式** | 页面栈（pages.json） | History 模式 | History 模式 |
| **状态持久化** | 微信本地存储 | localStorage | localStorage |
| **可视化** | 简单图表 | ECharts 雷达图 | ECharts + 数据大屏 |
| **特色能力** | 扫码、拍照、位置 | 文件上传、日历 | 实时数据、导出报表 |

## API 类型共享

后端已配置 OpenAPI/Swagger，前端通过 `@campus/shared` 包统一管理 API 类型：

```typescript
import type { Activity, ActivityCreateRequest } from '@campus/shared';
import { ActivityStatus, formatDateTime } from '@campus/shared';
```

## 状态管理

采用 Pinia 进行状态管理，按功能模块划分 Store：

```
stores/
├── user.ts      # 用户状态（token、profile、permissions）
├── activity.ts  # 活动状态
└── ...
```

## 与后端对接

后端 API 文档地址：`http://localhost:8080/docs`

共享类型定义位于 `packages/shared/src/api/types/` 目录。

## 开发规范

### 代码风格

- 使用 TypeScript 进行类型检查
- 遵循 Vue 3 Composition API 风格
- 组件名使用 PascalCase
- 组合式函数使用 useXxx 命名

### Git 提交规范

- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

## 部署

### Nginx 配置示例

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
    
    # API 代理
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

*文档版本：1.0*
*最后更新：2026-04-13*
