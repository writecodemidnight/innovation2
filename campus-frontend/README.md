# 校园社团活动评估系统 - 前端项目

基于大数据分析的校园社团活动效果评估与资源优化配置系统前端项目。

## 技术架构

采用 **Monorepo** 架构，使用 pnpm workspace 管理多个包：

| 包名 | 技术栈 | 目标平台 | 说明 |
|------|--------|----------|------|
| `@campus/shared` | TypeScript 5.3 | 全端共享 | API类型、工具函数、常量 |
| `@campus/student` | uni-app + Vue 3.4 | 微信小程序 | 学生端 - 活动发现、报名、评价 |
| `@campus/club` | Vue 3.4 + Vite 5 | PC浏览器 | 社团端 - 活动申报、资源预约 |
| `@campus/admin` | Vue 3.4 + Vite 5 | PC浏览器（大屏） | 管理端 - 审批、监控、决策 |

## 快速开始

### 环境要求

- Node.js >= 18.0.0
- pnpm >= 8.0.0

### 安装依赖

```bash
pnpm install
```

### 开发模式

```bash
# 启动学生端（微信小程序）
pnpm dev:student

# 启动社团端
pnpm dev:club

# 启动管理端
pnpm dev:admin
```

### 构建

```bash
# 构建所有包
pnpm build

# 构建单个包
pnpm build:student
pnpm build:club
pnpm build:admin
```

## 项目结构

```
campus-frontend/
├── packages/
│   ├── shared/          # 共享包
│   ├── student/         # 学生端（uni-app）
│   ├── club/            # 社团端（Vue3）
│   └── admin/           # 管理端（Vue3）
├── scripts/             # 构建脚本
├── package.json         # 根配置
└── pnpm-workspace.yaml  # pnpm工作区配置
```

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

## 与后端对接

后端 API 文档地址：`http://localhost:8080/docs`

共享类型定义位于 `packages/shared/src/api/types/` 目录。

## 许可证

MIT
