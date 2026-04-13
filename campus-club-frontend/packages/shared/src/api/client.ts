import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios';
import type { ApiResponse } from './types/index.js';

/**
 * 创建API客户端实例
 * @param baseURL - API基础URL
 * @param config - 额外配置
 */
export function createApiClient(baseURL: string, config?: AxiosRequestConfig): AxiosInstance {
  const client = axios.create({
    baseURL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
    ...config,
  });

  // 请求拦截器 - 添加Token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token') || uni?.getStorageSync?.('token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // 响应拦截器 - 统一处理
  client.interceptors.response.use(
    (response: AxiosResponse<ApiResponse<unknown>>) => {
      const { data } = response;

      if (data.code !== 'SUCCESS') {
        return Promise.reject(new Error(data.message || '请求失败'));
      }

      return response;
    },
    (error) => {
      // 统一错误处理
      const message = error.response?.data?.message || error.message || '网络错误';
      return Promise.reject(new Error(message));
    }
  );

  return client;
}

/**
 * 默认API客户端（浏览器端）
 */
export const apiClient = createApiClient(
  typeof window !== 'undefined'
    ? (import.meta.env?.VITE_API_BASE_URL || '/api')
    : '/api'
);

export default apiClient;
