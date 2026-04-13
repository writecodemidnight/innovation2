# 校园社团活动效果评估与资源优化配置系统 - 前端

基于大数据分析的校园社团活动效果评估与资源优化配置系统前端项目。

## 技术栈

- **框架**: uni-app (Vue 3) + TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **UI组件**: uView UI
- **代码规范**: ESLint + Prettier + Husky
- **开发语言**: TypeScript + SCSS

## 项目结构

```
src/
├── common/           # 公共资源
│   ├── styles/      # 全局样式
│   ├── utils/       # 工具函数
│   ├── constants/   # 常量定义
│   └── config/      # 配置文件
├── components/      # 公共组件库
├── pages/          # 页面组件
│   ├── student/    # 学生端页面
│   ├── club/       # 社团端页面
│   └── admin/      # 管理端页面
├── store/          # Pinia状态管理
├── api/            # API接口管理
├── types/          # TypeScript类型定义
└── hooks/          # 自定义组合式函数
```

## 开发环境

### 环境要求

- Node.js 18+
- npm 9+ 或 yarn 1.22+
- Git

### 安装依赖

```bash
npm install
```

### 开发运行

- **H5开发** (PC端): `npm run dev:h5`
- **微信小程序**: `npm run dev:mp-weixin`

### 构建

- **H5生产构建**: `npm run build:h5`
- **微信小程序构建**: `npm run build:mp-weixin`

### 代码质量

- **类型检查**: `npm run type-check`
- **代码格式化**: `npm run format`
- **代码检查**: `npm run lint`

## 功能模块

### 用户端划分

1. **学生端** - 活动推荐、报名、评价、个人中心
2. **社团端** - 活动申报、资源申请、效果分析、成员管理
3. **管理端** - 数据监控、资源管理、智能审批、系统配置

### 核心功能

- 个性化活动推荐 (K-Means聚类分析)
- 活动效果五维评估模型 (AHP + 模糊综合评价)
- 资源智能调度 (遗传算法优化)
- 多源数据融合 (ETL + 数据仓库)
- 实时数据监控大屏 (Tableau可视化)

## 开发规范

### Git提交规范

- feat: 新功能
- fix: 修复问题
- docs: 文档更新
- style: 代码格式
- refactor: 代码重构
- test: 测试相关
- chore: 构建工具或依赖更新

### 代码风格

- 使用TypeScript严格模式
- 组件使用组合式API (Composition API)
- 遵循Vue 3最佳实践
- 使用SCSS进行样式编写

## 配置说明

### 环境变量

- `.env.development` - 开发环境
- `.env.test` - 测试环境
- `.env.production` - 生产环境

### uni-app配置

- `pages.json` - 页面配置
- `manifest.json` - 应用配置
- `src/uni.scss` - 全局样式变量

## 部署说明

### H5部署

1. 运行 `npm run build:h5`
2. 将 `dist/build/h5` 目录部署到Web服务器

### 小程序部署

1. 运行 `npm run build:mp-weixin`
2. 使用微信开发者工具导入 `dist/build/mp-weixin`

## 相关链接

- [uni-app官方文档](https://uniapp.dcloud.net.cn/)
- [Vue 3文档](https://vuejs.org/)
- [TypeScript文档](https://www.typescriptlang.org/)
- [uView UI文档](https://uviewui.com/)
- [Pinia文档](https://pinia.vuejs.org/)

## 许可证

本项目仅供学习交流使用。
