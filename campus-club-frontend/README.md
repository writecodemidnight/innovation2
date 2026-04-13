# 校园社团活动评估系统 - 前端

基于大数据分析的校园社团活动效果评估与资源优化配置系统前端Monorepo。

## 项目结构

```
campus-club-frontend/
├── packages/
│   ├── shared/          # 共享包（API类型、常量、工具函数）
│   ├── student/         # 学生端（uni-app + Vant → 微信小程序）
│   ├── club/            # 社团端（Vue3 + Element Plus）
│   └── admin/           # 管理端（Vue3 + Element Plus + 大屏）
├── package.json
├── pnpm-workspace.yaml
└── tsconfig.json
```

## 快速开始

### 环境要求
- Node.js >= 18.0.0
- pnpm >= 8.0.0

### 安装依赖

```bash
pnpm install
```

### 开发各端

```bash
# 学生端（微信小程序）
pnpm dev:student

# 社团端（PC浏览器）
pnpm dev:club

# 管理端（PC浏览器 - 数据大屏）
pnpm dev:admin
```

### 构建生产环境

```bash
# 构建所有包
pnpm build

# 构建单个包
pnpm build:student
pnpm build:club
pnpm build:admin
```

## 技术栈

| 包名 | 技术栈 | 目标平台 |
|------|--------|----------|
| `@campus/shared` | TypeScript 5.3 | 全端共享 |
| `@campus/student` | uni-app + Vue 3.4 + Vant 4 | 微信小程序 |
| `@campus/club` | Vue 3.4 + Element Plus 2.5 | PC浏览器 |
| `@campus/admin` | Vue 3.4 + Element Plus 2.5 + ECharts | PC浏览器（大屏） |

## 开发规范

### 代码风格
- 使用TypeScript严格模式
- 组件使用Composition API
- 共享类型定义在 `@campus/shared` 包中

### 提交规范
- 功能开发：`feat: 描述`
- Bug修复：`fix: 描述`
- 文档更新：`docs: 描述`
- 重构：`refactor: 描述`

## 部署

### 构建产物

- `packages/student/dist/` → 微信小程序（需上传微信开发者工具）
- `packages/club/dist/` → Nginx静态托管
- `packages/admin/dist/` → Nginx静态托管

### Nginx配置示例

```nginx
server {
    listen 80;
    server_name campus-club.edu.cn;
    
    location /club {
        alias /usr/share/nginx/html/club;
        try_files $uri $uri/ /club/index.html;
    }
    
    location /admin {
        alias /usr/share/nginx/html/admin;
        try_files $uri $uri/ /admin/index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8080;
    }
}
```

## 文档

- [架构设计文档](../../docs/superpowers/specs/2026-04-13-frontend-architecture-design.md)
