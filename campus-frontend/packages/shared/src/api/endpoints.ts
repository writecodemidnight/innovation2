/**
 * API端点常量定义
 * 集中管理所有API路径
 */

// 使用硬编码 baseURL 避免 import.meta 导致小程序构建问题
// 在 vite.config.ts 中配置 proxy 即可
const API_BASE_URL = '/api/v1';

export const Endpoints = {
  // 认证相关
  auth: {
    login: `${API_BASE_URL}/auth/login`,
    logout: `${API_BASE_URL}/auth/logout`,
    wxLogin: `${API_BASE_URL}/auth/wechat-login`,
    wxBind: `${API_BASE_URL}/auth/wx-bind`,
    refresh: `${API_BASE_URL}/auth/refresh`,
    profile: `${API_BASE_URL}/auth/profile`,
    changePassword: `${API_BASE_URL}/auth/change-password`,
  },

  // 用户相关
  users: {
    list: `${API_BASE_URL}/users`,
    detail: (id: number) => `${API_BASE_URL}/users/${id}`,
    me: `${API_BASE_URL}/users/me`,
    updateMe: `${API_BASE_URL}/users/me`,
    create: `${API_BASE_URL}/users`,
    update: (id: number) => `${API_BASE_URL}/users/${id}`,
    delete: (id: number) => `${API_BASE_URL}/users/${id}`,
    stats: (id: number) => `${API_BASE_URL}/users/${id}/stats`,
  },

  // 活动相关
  activities: {
    list: `${API_BASE_URL}/activities`,
    detail: (id: number) => `${API_BASE_URL}/activities/${id}`,
    create: `${API_BASE_URL}/activities`,
    update: (id: number) => `${API_BASE_URL}/activities/${id}`,
    delete: (id: number) => `${API_BASE_URL}/activities/${id}`,
    join: (id: number) => `${API_BASE_URL}/activities/${id}/register`,
    leave: (id: number) => `${API_BASE_URL}/activities/${id}/cancel`,
    evaluate: (id: number) => `${API_BASE_URL}/activities/${id}/evaluate`,
    evaluations: (id: number) => `${API_BASE_URL}/activities/${id}/evaluations`,
    recommend: `${API_BASE_URL}/activities/recommend`,
    hot: `${API_BASE_URL}/activities/hot`,
    upcoming: `${API_BASE_URL}/activities/upcoming`,
  },

  // 社团相关
  clubs: {
    list: `${API_BASE_URL}/clubs`,
    detail: (id: number) => `${API_BASE_URL}/clubs/${id}`,
    my: `${API_BASE_URL}/clubs/my`,
    create: `${API_BASE_URL}/clubs`,
    update: (id: number) => `${API_BASE_URL}/clubs/${id}`,
    delete: (id: number) => `${API_BASE_URL}/clubs/${id}`,
    members: (id: number) => `${API_BASE_URL}/clubs/${id}/members`,
    stats: (id: number) => `${API_BASE_URL}/clubs/${id}/stats`,
    activities: (id: number) => `${API_BASE_URL}/clubs/${id}/activities`,
  },

  // 资源相关
  resources: {
    list: `${API_BASE_URL}/resources`,
    detail: (id: number) => `${API_BASE_URL}/resources/${id}`,
    create: `${API_BASE_URL}/resources`,
    update: (id: number) => `${API_BASE_URL}/resources/${id}`,
    delete: (id: number) => `${API_BASE_URL}/resources/${id}`,
    reserve: `${API_BASE_URL}/resources/reserve`,
    reservations: `${API_BASE_URL}/resources/reservations`,
    myReservations: `${API_BASE_URL}/resources/my-reservations`,
    cancelReservation: (id: number) => `${API_BASE_URL}/resources/reservations/${id}/cancel`,
    approveReservation: (id: number) => `${API_BASE_URL}/resources/reservations/${id}/approve`,
    rejectReservation: (id: number) => `${API_BASE_URL}/resources/reservations/${id}/reject`,
    availability: (id: number) => `${API_BASE_URL}/resources/${id}/availability`,
    heatmap: `${API_BASE_URL}/resources/heatmap`,
  },

  // 评估相关
  evaluation: {
    report: (activityId: number) => `${API_BASE_URL}/evaluation/${activityId}/report`,
    radar: (activityId: number) => `${API_BASE_URL}/evaluation/${activityId}/radar`,
    history: `${API_BASE_URL}/evaluation/history`,
    compare: `${API_BASE_URL}/evaluation/compare`,
  },

  // 仪表盘/统计相关
  dashboard: {
    overview: `${API_BASE_URL}/dashboard/overview`,
    statistics: `${API_BASE_URL}/dashboard/stats`,
    trends: `${API_BASE_URL}/dashboard/trends`,
    alerts: `${API_BASE_URL}/dashboard/alerts`,
    realtime: `${API_BASE_URL}/dashboard/realtime`,
  },

  // 审批相关
  approval: {
    pending: `${API_BASE_URL}/approval/pending`,
    history: `${API_BASE_URL}/approval/history`,
    approve: (id: number) => `${API_BASE_URL}/approval/${id}/approve`,
    reject: (id: number) => `${API_BASE_URL}/approval/${id}/reject`,
  },

  // 管理端 - Dashboard
  adminDashboard: {
    stats: `${API_BASE_URL}/admin/dashboard/stats`,
    activityTrends: `${API_BASE_URL}/admin/dashboard/activity-trends`,
    clubRankings: `${API_BASE_URL}/admin/dashboard/club-rankings`,
    resourceUsage: `${API_BASE_URL}/admin/dashboard/resource-usage`,
    pendingTasks: `${API_BASE_URL}/admin/dashboard/pending-tasks`,
  },

  // 管理端 - 审批
  adminApprovals: {
    counts: `${API_BASE_URL}/admin/approvals/counts`,
    pendingActivities: `${API_BASE_URL}/admin/approvals/activities/pending`,
    approveActivity: (id: number) => `${API_BASE_URL}/admin/approvals/activities/${id}/approve`,
    rejectActivity: (id: number) => `${API_BASE_URL}/admin/approvals/activities/${id}/reject`,
    pendingResourceBookings: `${API_BASE_URL}/admin/approvals/resource-bookings/pending`,
    approveResourceBooking: (id: number) => `${API_BASE_URL}/admin/approvals/resource-bookings/${id}/approve`,
    rejectResourceBooking: (id: number) => `${API_BASE_URL}/admin/approvals/resource-bookings/${id}/reject`,
    pendingFundApplications: `${API_BASE_URL}/funds/applications/pending`,
    approveFundApplication: (id: number) => `${API_BASE_URL}/funds/applications/${id}/approve`,
    rejectFundApplication: (id: number) => `${API_BASE_URL}/funds/applications/${id}/reject`,
  },

  // 管理端 - 审批历史
  adminHistory: {
    counts: `${API_BASE_URL}/admin/history/counts`,
    activities: `${API_BASE_URL}/admin/history/activities`,
    resourceBookings: `${API_BASE_URL}/admin/history/resource-bookings`,
    fundApplications: `${API_BASE_URL}/admin/history/fund-applications`,
  },

  // 管理端 - 资源池管理
  adminResources: {
    list: `${API_BASE_URL}/admin/resources`,
    detail: (id: number) => `${API_BASE_URL}/admin/resources/${id}`,
    create: `${API_BASE_URL}/admin/resources`,
    update: (id: number) => `${API_BASE_URL}/admin/resources/${id}`,
    delete: (id: number) => `${API_BASE_URL}/admin/resources/${id}`,
    stats: `${API_BASE_URL}/admin/resources/stats`,
  },

  // AI/智能相关
  ai: {
    optimize: `${API_BASE_URL}/ai/optimize`,
    schedule: `${API_BASE_URL}/ai/schedule`,
    insights: `${API_BASE_URL}/ai/insights`,
    predict: `${API_BASE_URL}/ai/predict`,
  },

  // 文件上传
  upload: {
    image: `${API_BASE_URL}/upload/image`,
    file: `${API_BASE_URL}/upload/file`,
    avatar: `${API_BASE_URL}/upload/avatar`,
  },

  // 资金申请相关
  funds: {
    applications: `${API_BASE_URL}/funds/applications`,
    myApplications: `${API_BASE_URL}/funds/applications/my`,
    clubApplications: `${API_BASE_URL}/funds/applications/club`,
    applicationDetail: (id: number) => `${API_BASE_URL}/funds/applications/${id}`,
    cancel: (id: number) => `${API_BASE_URL}/funds/applications/${id}/cancel`,
    approve: (id: number) => `${API_BASE_URL}/funds/applications/${id}/approve`,
    reject: (id: number) => `${API_BASE_URL}/funds/applications/${id}/reject`,
    pending: `${API_BASE_URL}/funds/applications/pending`,
  },

  // 反馈评价相关
  feedback: {
    list: `${API_BASE_URL}/feedback`,
    my: `${API_BASE_URL}/feedback/my`,
    detail: (id: number) => `${API_BASE_URL}/feedback/${id}`,
    create: `${API_BASE_URL}/feedback`,
    update: (id: number) => `${API_BASE_URL}/feedback/${id}`,
    delete: (id: number) => `${API_BASE_URL}/feedback/${id}`,
    byActivity: (activityId: number) => `${API_BASE_URL}/feedback/activity/${activityId}`,
    stats: (activityId: number) => `${API_BASE_URL}/feedback/activity/${activityId}/stats`,
  },
} as const;

export default Endpoints;
