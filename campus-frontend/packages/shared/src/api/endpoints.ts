/**
 * API端点常量定义
 * 集中管理所有API路径
 */

const API_BASE_URL = typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL
  ? import.meta.env.VITE_API_BASE_URL
  : '/api';

export const Endpoints = {
  // 认证相关
  auth: {
    login: `${API_BASE_URL}/auth/login`,
    logout: `${API_BASE_URL}/auth/logout`,
    wxLogin: `${API_BASE_URL}/auth/wx-login`,
    wxBind: `${API_BASE_URL}/auth/wx-bind`,
    refresh: `${API_BASE_URL}/auth/refresh`,
    profile: `${API_BASE_URL}/auth/profile`,
    changePassword: `${API_BASE_URL}/auth/change-password`,
  },

  // 用户相关
  users: {
    list: `${API_BASE_URL}/users`,
    detail: (id: number) => `${API_BASE_URL}/users/${id}`,
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
    join: (id: number) => `${API_BASE_URL}/activities/${id}/join`,
    leave: (id: number) => `${API_BASE_URL}/activities/${id}/leave`,
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
    statistics: `${API_BASE_URL}/dashboard/statistics`,
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
} as const;

export default Endpoints;
