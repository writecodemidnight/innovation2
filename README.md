# 校园社团活动效果评估与资源优化配置系统

<p align="center">
  <img src="https://img.shields.io/badge/Spring%20Boot-3.2-blue" alt="Spring Boot">
  <img src="https://img.shields.io/badge/FastAPI-0.109-green" alt="FastAPI">
  <img src="https://img.shields.io/badge/Vue%203-3.4-brightgreen" alt="Vue 3">
  <img src="https://img.shields.io/badge/uni--app-3.0-orange" alt="uni-app">
  <img src="https://img.shields.io/badge/Python-3.10-blue" alt="Python">
  <img src="https://img.shields.io/badge/Java-21-orange" alt="Java">
</p>

基于大数据分析的校园社团活动效果评估与资源优化配置系统。通过整合多源数据，运用机器学习算法，为校园社团管理提供数据驱动的决策支持。

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端层                                    │
├──────────────┬──────────────┬──────────────────────────────────┤
│  学生端小程序  │  社团端Web    │  管理端大屏                       │
│  (uni-app)   │  (Vue 3)     │   (Vue 3)                        │
└──────────────┴──────────────┴──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         后端层                                    │
├──────────────────────────────┬──────────────────────────────────┤
│    Java Spring Boot (主服务)  │   Python FastAPI (算法服务)       │
│                              │                                  │
│  • RESTful API               │  • K-Means 聚类分析               │
│  • 业务逻辑                  │  • AHP 层次分析法                 │
│  • 权限管理                  │  • LSTM 预测模型                  │
│  • 数据持久化                │  • NLP 情感分析                   │
└──────────────────────────────┴──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         数据层                                    │
├──────────────┬──────────────┬──────────────────────────────────┤
│  PostgreSQL  │    Redis     │     阿里云OSS                     │
│  (主数据库)   │   (缓存)      │     (文件存储)                   │
└──────────────┴──────────────┴──────────────────────────────────┘
```

---

## 项目结构

```
innovation-main/
├── campus-main/                    # Java Spring Boot 主服务
│   ├── src/main/java/com/campusclub/
│   │   ├── activity/               # 活动管理模块
│   │   ├── club/                   # 社团管理模块
│   │   ├── evaluation/             # 评估分析模块
│   │   ├── resource/               # 资源管理模块
│   │   ├── user/                   # 用户管理模块
│   │   └── fund/                   # 资金管理模块
│   └── src/main/resources/
│       └── application.yml         # 主配置文件
│
├── campus-ai/                      # Python FastAPI 算法服务
│   ├── src/
│   │   ├── api/                    # API 路由
│   │   │   └── v3/                 # v3 版本接口
│   │   │       ├── clustering.py   # K-Means 聚类
│   │   │       ├── evaluation.py   # AHP 评估
│   │   │       ├── scheduling.py   # GA/LSTM 调度
│   │   │       └── tasks.py        # 异步任务
│   │   ├── algorithms/             # 算法实现
│   │   └── core/                   # 核心工具
│   └── requirements.txt
│
├── campus-frontend/                # 前端项目 (Monorepo)
│   ├── packages/
│   │   ├── shared/                 # 共享类型和工具
│   │   ├── student/                # 学生端小程序
│   │   ├── club/                   # 社团端 Web
│   │   └── admin/                  # 管理端大屏
│   └── package.json
│
└── docs/                           # 项目文档
    ├── development/                # 开发文档
    ├── tech-debt/                  # 技术债务
    └── superpowers/                # 架构设计
```

---

## 核心功能

### 1. 活动效果评估
- **AHP 五维评估模型**: 参与度、教育性、创新性、影响力、可持续性
- **雷达图可视化**: 直观展示活动各维度表现
- **历史趋势分析**: 追踪活动质量变化趋势

### 2. 智能资源调度
- **LSTM 需求预测**: 预测未来资源需求
- **GA 遗传算法优化**: 自动优化资源分配方案
- **冲突检测**: 智能识别资源预约冲突

### 3. 社团聚类分析
- **K-Means 自动分类**: 基于特征相似度自动分组
- **个性化推荐**: 为学生推荐感兴趣的社团和活动
- **社团画像**: 生成社团特征标签

### 4. 智能审批辅助
- **风险评估**: 预测活动成功率
- **资源建议**: AI 推荐最佳资源配置
- **一键审批**: 快速处理常规申请

---

## 快速开始

### 环境要求

| 组件 | 版本要求 |
|------|----------|
| Java | 21+ |
| Python | 3.10+ |
| Node.js | 18+ |
| PostgreSQL | 14+ |
| Redis | 6+ |

### 1. 启动后端服务 (Java)

```bash
cd campus-main
# 配置数据库连接 (src/main/resources/application-local.yml)
mvn spring-boot:run -Dspring-boot.run.profiles=local
```

服务启动后访问: http://localhost:8080/swagger-ui.html

### 2. 启动算法服务 (Python)

```bash
cd campus-ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问: http://localhost:8000/docs

### 3. 启动前端

```bash
cd campus-frontend
pnpm install

# 启动社团端
pnpm dev:club

# 启动管理端
pnpm dev:admin

# 启动学生端(小程序)
pnpm dev:student
```

---

## 主要技术栈

### 后端 (Java)
- **框架**: Spring Boot 3.2
- **安全**: Spring Security + JWT
- **数据**: Spring Data JPA + QueryDSL
- **数据库**: PostgreSQL + Redis
- **文档**: SpringDoc OpenAPI

### 算法服务 (Python)
- **框架**: FastAPI
- **ML/AI**: PyTorch, Scikit-learn, Transformers
- **数据处理**: Pandas, NumPy
- **异步**: Celery + Redis

### 前端
- **社团/管理端**: Vue 3.4 + Vite 5 + Element Plus
- **学生端**: uni-app 3.0 (微信小程序)
- **类型**: TypeScript 5.3
- **状态**: Pinia

---

## 开发文档

| 文档 | 说明 |
|------|------|
| [开发指南](docs/development/PROJECT_COMPLETION_GUIDE.md) | 开发任务清单和进度 |
| [技术债务](docs/tech-debt/CRITICAL_ISSUES.md) | 紧急修复事项 |
| [API 接口](docs/api/README.md) | 接口文档汇总 |
| [数据库设计](docs/database/README.md) | 数据库表结构 |

---

## 算法模型说明

### AHP 五维评估权重

| 维度 | 权重 | 说明 |
|------|------|------|
| 参与度 | 0.32 | 学生参与程度 |
| 教育性 | 0.18 | 教育价值 |
| 创新性 | 0.15 | 创新程度 |
| 影响力 | 0.22 | 社会/校园影响 |
| 可持续性 | 0.13 | 活动可持续性 |

### K-Means 聚类特征

- 社团规模
- 活动频率
- 成员活跃度
- 活动类型分布
- 历史评分

---

## 贡献指南

1. Fork 项目
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add some amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

### 提交规范

- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- 项目维护者: 校园社团系统开发团队
- 问题反馈: GitHub Issues
