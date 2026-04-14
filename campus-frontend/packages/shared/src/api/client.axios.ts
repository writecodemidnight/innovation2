/**
 * Axios API客户端封装
 * 用于PC浏览器环境（社团端）
 */

import axios from 'axios';
import type { ApiResponse } from './types';

// 创建axios实例
const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：添加Authorization头
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：统一错误处理
axiosClient.interceptors.response.use(
  (response) => {
    const data = response.data as ApiResponse<any>;
    if (data.code !== 'SUCCESS' && data.code !== '200') {
      // 业务错误
      const error = new Error(data.message || '请求失败');
      (error as any).code = data.code;
      return Promise.reject(error);
    }
    return data.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，清除并跳转登录
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/club/login';
    }
    return Promise.reject(error);
  }
);

// 导出apiClient
export const apiClient = {
  get: <T>(url: string, config?: any) => axiosClient.get<T>(url, config).then(res => res.data),
  post: <T>(url: string, data?: any, config?: any) => axiosClient.post<T>(url, data, config).then(res => res.data),
  put: <T>(url: string, data?: any, config?: any) => axiosClient.put<T>(url, data, config).then(res => res.data),
  delete: <T>(url: string, config?: any) => axiosClient.delete<T>(url, config).then(res => res.data),
};

export type ApiClient = typeof apiClient;
