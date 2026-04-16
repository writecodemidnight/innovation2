/**
 * Axios API客户端封装
 * 用于PC浏览器环境（社团端）
 */

import axios from 'axios';
import type { ApiResponse } from './types';

// 内存中缓存token，避免每次请求都读取localStorage
let cachedToken: string | null = null;

// 从localStorage读取token
const getToken = (): string | null => {
  if (cachedToken === null) {
    cachedToken = localStorage.getItem('access_token');
  }
  return cachedToken;
};

// 清除缓存的token
export const clearTokenCache = (): void => {
  cachedToken = null;
};

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
    const token = getToken();
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
      clearTokenCache();
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      // 根据当前路径判断跳转的登录页
      const currentPath = window.location.pathname;
      const loginPath = currentPath.startsWith('/admin') ? '/admin/login' : '/club/login';
      window.location.href = loginPath;
    }
    return Promise.reject(error);
  }
);

// 导出 axiosApiClient with correct return types (data only, not AxiosResponse)
export const axiosApiClient = {
  get: <T>(url: string, config?: any): Promise<T> => axiosClient.get(url, config),
  post: <T>(url: string, data?: any, config?: any): Promise<T> => axiosClient.post(url, data, config),
  put: <T>(url: string, data?: any, config?: any): Promise<T> => axiosClient.put(url, data, config),
  delete: <T>(url: string, config?: any): Promise<T> => axiosClient.delete(url, config),
  patch: <T>(url: string, data?: any, config?: any): Promise<T> => axiosClient.patch(url, data, config),
};

// 兼容旧代码的别名导出
export const apiClient = axiosApiClient;

export type ApiClient = typeof axiosApiClient;
