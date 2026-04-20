# 管理端前端开发指南

## 已完成内容

### 1. API 类型定义 (@campus/shared)

#### 管理端仪表盘类型 (`adminDashboard.ts`)
- `AdminDashboardStats` - 全局统计数据
- `ActivityTrend` - 活动趋势
- `ClubRanking` - 社团排行
- `ResourceUsage` - 资源使用
- `PendingTasks` - 待办任务

#### 管理端审批类型 (`adminApproval.ts`)
- `ApprovalStatus` - 审批状态
- `ApprovalType` - 审批类型
- `ApprovalRequest` - 审批请求
- `ApprovalCounts` - 审批统计
- `HistoryCounts` - 历史统计
- `ResourceBooking` - 资源预约

#### 管理端资源类型 (`adminResource.ts`)
- `AdminResource` - 资源实体
- `ResourceRequest` - 资源请求
- `ResourceStats` - 资源统计

### 2. API 端点 (@campus/shared)

在 `endpoints.ts` 中新增：

```typescript
// 管理端 - Dashboard
adminDashboard: {
  stats: '/api/v1/admin/dashboard/stats',
  activityTrends: '/api/v1/admin/dashboard/activity-trends',
  clubRankings: '/api/v1/admin/dashboard/club-rankings',
  resourceUsage: '/api/v1/admin/dashboard/resource-usage',
  pendingTasks: '/api/v1/admin/dashboard/pending-tasks',
},

// 管理端 - 审批
adminApprovals: {
  counts: '/api/v1/admin/approvals/counts',
  pendingActivities: '/api/v1/admin/approvals/activities/pending',
  approveActivity: (id) => `/api/v1/admin/approvals/activities/${id}/approve`,
  rejectActivity: (id) => `/api/v1/admin/approvals/activities/${id}/reject`,
  pendingResourceBookings: '/api/v1/admin/approvals/resource-bookings/pending',
  approveResourceBooking: (id) => `/api/v1/admin/approvals/resource-bookings/${id}/approve`,
  rejectResourceBooking: (id) => `/api/v1/admin/approvals/resource-bookings/${id}/reject`,
  pendingFundApplications: '/api/v1/funds/applications/pending',
  approveFundApplication: (id) => `/api/v1/funds/applications/${id}/approve`,
  rejectFundApplication: (id) => `/api/v1/funds/applications/${id}/reject`,
},

// 管理端 - 审批历史
adminHistory: {
  counts: '/api/v1/admin/history/counts',
  activities: '/api/v1/admin/history/activities',
  resourceBookings: '/api/v1/admin/history/resource-bookings',
  fundApplications: '/api/v1/admin/history/fund-applications',
},

// 管理端 - 资源池
adminResources: {
  list: '/api/v1/admin/resources',
  detail: (id) => `/api/v1/admin/resources/${id}`,
  create: '/api/v1/admin/resources',
  update: (id) => `/api/v1/admin/resources/${id}`,
  delete: (id) => `/api/v1/admin/resources/${id}`,
  stats: '/api/v1/admin/resources/stats',
},
```

### 3. Pinia Stores (@campus/admin)

#### Dashboard Store (`dashboard.ts`)
```typescript
const store = useDashboardStore()

// Actions
store.fetchStats()           // 获取统计数据
store.fetchActivityTrends()  // 获取活动趋势
store.fetchClubRankings()    // 获取社团排行
store.fetchResourceUsage()   // 获取资源使用
store.fetchPendingTasks()    // 获取待办任务
store.loadAllDashboardData() // 加载所有数据

// State
store.stats           // 统计数据
store.activityTrends  // 活动趋势
store.clubRankings    // 社团排行
store.resourceUsage   // 资源使用
store.pendingTasks    // 待办任务
store.loading         // 加载状态
```

#### Approval Store (`approval.ts`)
```typescript
const store = useApprovalStore()

// 待审批统计
store.fetchApprovalCounts()

// 活动审批
store.fetchPendingActivities()
store.approveActivity(id, comment)
store.rejectActivity(id, comment)

// 资源预约审批
store.fetchPendingResourceBookings()
store.approveResourceBooking(id, comment)
store.rejectResourceBooking(id, comment)

// 资金申请审批
store.fetchPendingFundApplications()
store.approveFundApplication(id, comment)
store.rejectFundApplication(id, comment)

// 审批历史
store.fetchHistoryCounts()
```

#### Resource Store (`resource.ts`)
```typescript
const store = useResourceStore()

// 统计
store.fetchStats()

// CRUD
store.fetchResources(page, size, type, status)
store.fetchResourceDetail(id)
store.createResource(data)
store.updateResource(id, data)
store.deleteResource(id)
```

## 使用示例

### 在 Vue 组件中使用

```vue
<script setup lang="ts">
import { useDashboardStore, useApprovalStore } from '@/stores'

const dashboardStore = useDashboardStore()
const approvalStore = useApprovalStore()

// 加载Dashboard数据
onMounted(() => {
  dashboardStore.loadAllDashboardData()
  approvalStore.fetchApprovalCounts()
})

// 使用数据
const stats = computed(() => dashboardStore.stats)
const pendingTotal = computed(() => approvalStore.totalPending)
</script>
```

## 文件清单

### 新建文件
- `campus-frontend/packages/shared/src/api/types/adminDashboard.ts`
- `campus-frontend/packages/shared/src/api/types/adminApproval.ts`
- `campus-frontend/packages/shared/src/api/types/adminResource.ts`
- `campus-frontend/packages/admin/src/stores/dashboard.ts`
- `campus-frontend/packages/admin/src/stores/approval.ts`
- `campus-frontend/packages/admin/src/stores/resource.ts`
- `campus-frontend/packages/admin/src/stores/index.ts`

### 修改文件
- `campus-frontend/packages/shared/src/api/types/index.ts`
- `campus-frontend/packages/shared/src/api/endpoints.ts`
