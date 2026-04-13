/**
 * API端点常量定义
 * 与后端Swagger/OpenAPI定义保持一致
 */

const API_BASE_URL = typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL
  ? import.meta.env.VITE_API_BASE_URL
  : '/api';

export const Endpoints = {
  // 认证相关
  auth: {
    login: `${API_BASE_URL}/auth/login`,
    wxLogin: `${API_BASE_URL}/auth/wx-login`,
    wxLoginByCode: `${API_BASE_URL}/auth/wx-login/code`,
    refresh: `${API_BASE_URL}/auth/refresh`,
    logout: `${API_BASE_URL}/auth/logout`,
    profile: `${API_BASE_URL}/auth/profile`,
    updateProfile: `${API_BASE_URL}/auth/profile`,
  },

  // 用户相关
  users: {
    list: `${API_BASE_URL}/users`,
    detail: (id: number) => `${API_BASE_URL}/users/${id}`,
    create: `${API_BASE_URL}/users`,
    update: (id: number) => `${API_BASE_URL}/users/${id}`,
    delete: (id: number) => `${API_BASE_URL}/users/${id}`,
  },

  // 社团相关
  clubs: {
    list: `${API_BASE_URL}/clubs`,
    detail: (id: number) => `${API_BASE_URL}/clubs/${id}`,
    create: `${API_BASE_URL}/clubs`,
    update: (id: number) => `${API_BASE_URL}/clubs/${id}`,
    delete: (id: number) => `${API_BASE_URL}/clubs/${id}`,
    members: (id: number) => `${API_BASE_URL}/clubs/${id}/members`,
    activities: (id: number) => `${API_BASE_URL}/clubs/${id}/activities`,
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
    checkIn: (id: number) => `${API_BASE_URL}/activities/${id}/check-in`,
    participants: (id: number) => `${API_BASE_URL}/activities/${id}/participants`,
    evaluate: (id: number) => `${API_BASE_URL}/activities/${id}/evaluate`,
    recommend: `${API_BASE_URL}/activities/recommend`,
    hot: `${API_BASE_URL}/activities/hot`,
    upcoming: `${API_BASE_URL}/activities/upcoming`,
  },

  // 资源相关
  resources: {
    list: `${API_BASE_URL}/resources`,
    detail: (id: number) => `${API_BASE_URL}/resources/${id}`,
    create: `${API_BASE_URL}/resources`,
    update: (id: number) => `${API_BASE_URL}/resources/${id}`,
    delete: (id: number) => `${API_BASE_URL}/resources/${id}`,
    reserve: `${API_BASE_URL}/resources/reservations`,
    myReservations: `${API_BASE_URL}/resources/my-reservations`,
    cancelReservation: (id: number) => `${API_BASE_URL}/resources/reservations/${id}/cancel`,
    approveReservation: (id: number) => `${API_BASE_URL}/resources/reservations/${id}/approve`,
    calendar: `${API_BASE_URL}/resources/calendar`,
  },

  // 评估相关
  evaluation: {
    submit: `${API_BASE_URL}/evaluation`,
    report: (activityId: number) => `${API_BASE_URL}/evaluation/${activityId}/report`,
    radar: (activityId: number) => `${API_BASE_URL}/evaluation/${activityId}/radar`,
    feedback: (activityId: number) => `${API_BASE_URL}/evaluation/${activityId}/feedback`,
    metrics: `${API_BASE_URL}/evaluation/metrics`,
  },

  // 算法服务代理
  algorithm: {
    recommend: `${API_BASE_URL}/algorithm/recommend`,
    evaluate: `${API_BASE_URL}/algorithm/evaluate`,
    predict: `${API_BASE_URL}/algorithm/predict`,
    optimize: `${API_BASE_URL}/algorithm/optimize`,
    sentiment: `${API_BASE_URL}/algorithm/sentiment`,
    imageQuality: `${API_BASE_URL}/algorithm/image-quality`,
  },

  // 管理端
  admin: {
    dashboard: `${API_BASE_URL}/admin/dashboard`,
    stats: `${API_BASE_URL}/admin/stats`,
    pendingApprovals: `${API_BASE_URL}/admin/approvals/pending`,
    approve: (id: number) => `${API_BASE_URL}/admin/approvals/${id}/approve`,
    reject: (id: number) => `${API_BASE_URL}/admin/approvals/${id}/reject`,
    logs: `${API_BASE_URL}/admin/logs`,
    configs: `${API_BASE_URL}/admin/configs`,
  },

  // 文件上传
  files: {
    upload: `${API_BASE_URL}/files/upload`,
    uploadImage: `${API_BASE_URL}/files/upload/image`,
    delete: (id: string) => `${API_BASE_URL}/files/${id}`,
  },
} as const;

export default Endpoints;
