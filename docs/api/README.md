# API 接口文档

本文档汇总了校园社团系统的所有 API 接口。

---

## 目录

1. [Java 后端 API](#java-后端-api)
2. [Python 算法服务 API](#python-算法服务-api)
3. [接口规范](#接口规范)

---

## Java 后端 API

### 基础信息

- **Base URL**: `http://localhost:8080`
- **文档地址**: `http://localhost:8080/swagger-ui.html`
- **认证方式**: Bearer Token (JWT)

### 用户模块

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 用户登录 | POST | `/api/v1/auth/login` | 用户名密码登录 |
| 用户注册 | POST | `/api/v1/auth/register` | 学生注册 |
| 获取当前用户 | GET | `/api/v1/users/me` | 获取登录用户信息 |
| 更新用户信息 | PUT | `/api/v1/users/me` | 更新个人信息 |

### 社团模块

| 接口 | 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|------|
| 获取社团列表 | GET | `/api/v1/clubs` | 公开 | 分页获取社团 |
| 获取社团详情 | GET | `/api/v1/clubs/{id}` | 公开 | 社团详细信息 |
| 创建社团 | POST | `/api/v1/clubs` | ADMIN | 新建社团 |
| 更新社团 | PUT | `/api/v1/clubs/{id}` | CLUB_MANAGER | 更新社团信息 |
| 获取我的社团 | GET | `/api/v1/clubs/my` | 需登录 | 获取所属社团 |
| 添加成员 | POST | `/api/v1/clubs/{id}/members` | CLUB_MANAGER | 添加社团成员 |

### 活动模块

| 接口 | 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|------|
| 获取活动列表 | GET | `/api/v1/activities` | 公开 | 分页获取活动 |
| 获取活动详情 | GET | `/api/v1/activities/{id}` | 公开 | 活动详细信息 |
| 创建活动 | POST | `/api/v1/activities` | CLUB_MANAGER | 申报新活动 |
| 更新活动 | PUT | `/api/v1/activities/{id}` | CLUB_MANAGER | 更新活动信息 |
| 删除活动 | DELETE | `/api/v1/activities/{id}` | CLUB_MANAGER | 取消活动 |
| 审批活动 | POST | `/api/v1/activities/{id}/approve` | ADMIN | 管理员审批 |
| 报名活动 | POST | `/api/v1/activities/{id}/register` | 学生 | 学生报名 |
| 获取报名列表 | GET | `/api/v1/activities/{id}/participants` | CLUB_MANAGER | 参与人员列表 |

### 资源模块

| 接口 | 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|------|
| 获取资源列表 | GET | `/api/v1/resources` | 公开 | 所有可用资源 |
| 按类型获取 | GET | `/api/v1/resources/type/{type}` | 公开 | 按类型筛选 |
| 获取资源详情 | GET | `/api/v1/resources/{id}` | 公开 | 资源详细信息 |
| 创建预约 | POST | `/api/v1/resources/bookings` | CLUB_MANAGER | 申请资源 |
| 我的预约 | GET | `/api/v1/resources/bookings/my` | 需登录 | 查询我的预约 |
| 取消预约 | POST | `/api/v1/resources/bookings/{id}/cancel` | CLUB_MANAGER | 取消预约 |

### 评估模块

| 接口 | 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|------|
| 提交评估 | POST | `/api/v1/activities/{id}/evaluation` | CLUB_MANAGER | 提交AHP评估 |
| 获取评估 | GET | `/api/v1/activities/{id}/evaluation` | CLUB_MANAGER | 获取评估报告 |
| 雷达图数据 | GET | `/api/v1/activities/{id}/evaluation/radar` | CLUB_MANAGER | 获取雷达图数据 |
| 提交反馈 | POST | `/api/v1/activities/{id}/feedback` | 学生 | 学生提交评价 |
| 获取反馈分析 | GET | `/api/v1/activities/{id}/feedback/analysis` | CLUB_MANAGER | NLP分析结果 |

### 资金模块

| 接口 | 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|------|
| 申请资金 | POST | `/api/v1/funds/applications` | CLUB_MANAGER | 提交经费申请 |
| 我的申请 | GET | `/api/v1/funds/applications/my` | CLUB_MANAGER | 查询申请记录 |
| 审批通过 | POST | `/api/v1/funds/applications/{id}/approve` | ADMIN | 管理员通过 |
| 审批拒绝 | POST | `/api/v1/funds/applications/{id}/reject` | ADMIN | 管理员拒绝 |

### 推荐模块

| 接口 | 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|------|
| 活动推荐 | GET | `/api/v1/recommendations/activities` | 学生 | 个性化推荐 |
| 社团推荐 | GET | `/api/v1/recommendations/clubs` | 学生 | 社团推荐 |

### 管理端大屏

| 接口 | 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|------|
| 数据概览 | GET | `/api/v1/dashboard/overview` | ADMIN | 全局统计数据 |
| 活动趋势 | GET | `/api/v1/dashboard/activity-trends` | ADMIN | 时间趋势 |
| 社团排行 | GET | `/api/v1/dashboard/club-rankings` | ADMIN | 排行榜 |
| 资源使用 | GET | `/api/v1/dashboard/resource-usage` | ADMIN | 资源统计 |

---

## Python 算法服务 API

### 基础信息

- **Base URL**: `http://localhost:8000`
- **文档地址**: `http://localhost:8000/docs`
- **无需认证** (内部服务)

### 健康检查

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 服务健康 | GET | `/health` | 检查服务状态 |
| AHP健康 | GET | `/api/v3/evaluation/health` | AHP服务状态 |

### AHP 评估接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| AHP评估 | POST | `/api/v3/evaluation/ahp` | 五维评估计算 |
| 获取权重 | GET | `/api/v3/evaluation/weights` | 获取AHP权重 |

**AHP评估请求示例**:
```json
{
  "scores": {
    "参与度": 85,
    "教育性": 90,
    "创新性": 75,
    "影响力": 80,
    "可持续性": 88
  }
}
```

**AHP评估响应示例**:
```json
{
  "success": true,
  "total_score": 84.23,
  "dimension_scores": {
    "参与度": 85,
    "教育性": 90,
    "创新性": 75,
    "影响力": 80,
    "可持续性": 88
  },
  "weights": {
    "参与度": 0.32,
    "教育性": 0.18,
    "创新性": 0.15,
    "影响力": 0.22,
    "可持续性": 0.13
  },
  "contributions": {
    "参与度": 27.2,
    "教育性": 16.2,
    "创新性": 11.25,
    "影响力": 17.6,
    "可持续性": 11.44
  },
  "consistency_ratio": 0.03,
  "consistency_check_passed": true,
  "algorithm_version": "AHP-v1.0"
}
```

### 聚类分析接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 社团聚类 | POST | `/api/v3/clustering/clubs` | K-Means社团聚类 |
| 学生聚类 | POST | `/api/v3/clustering/students` | 学生分群 |
| 获取聚类结果 | GET | `/api/v3/clustering/results/{task_id}` | 查询聚类结果 |

### 调度优化接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 资源预测 | POST | `/api/v3/scheduling/forecast` | LSTM需求预测 |
| 资源优化 | POST | `/api/v3/scheduling/optimize` | GA资源优化 |
| 获取预测结果 | GET | `/api/v3/scheduling/forecast/{task_id}` | 查询预测结果 |
| 获取优化结果 | GET | `/api/v3/scheduling/optimize/{task_id}` | 查询优化结果 |

### NLP分析接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 情感分析 | POST | `/api/v3/nlp/analyze` | 评价情感分析 |
| 关键词提取 | POST | `/api/v3/nlp/keywords` | 提取关键词 |

---

## 接口规范

### 通用响应格式

#### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": { }
}
```

#### 错误响应
```json
{
  "code": 400,
  "message": "参数错误",
  "error": "INVALID_PARAMETER"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 (Token无效或过期) |
| 403 | 禁止访问 (权限不足) |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 认证方式

所有需要认证的接口需在 Header 中携带 Token:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### 分页参数

列表接口支持统一分页参数:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 0 | 页码 (从0开始) |
| size | int | 20 | 每页大小 |
| sort | string | id,desc | 排序方式 |

### 分页响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "content": [ ],
    "totalElements": 100,
    "totalPages": 10,
    "number": 0,
    "size": 10,
    "first": true,
    "last": false
  }
}
```

---

## 接口版本说明

| 版本 | 状态 | 说明 |
|------|------|------|
| v1 | 当前 | 主版本，推荐使用 |
| v3 | 弃用 | Python算法服务内部版本，将被v2替代 |

---

## 变更日志

### 2024-04-15
- 新增资金申请接口
- 新增管理端大屏接口
- 新增推荐算法接口

### 2024-04-14
- 新增资源预约接口
- 新增AHP评估接口

### 2024-04-13
- 初始化API文档
