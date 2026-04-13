/**
 * API客户端封装
 * 基于axios的统一请求处理
 */

import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type AxiosError,
} from 'axios';
import type { ApiResponse } from './types';

// API配置接口
export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  withCredentials?: boolean;
}

// 创建API客户端
export function createApiClient(config: ApiClientConfig): AxiosInstance {
  const client = axios.create({
    baseURL: config.baseURL,
    timeout: config.timeout || 30000,
    withCredentials: config.withCredentials ?? true,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 请求拦截器
  client.interceptors.request.use(
    (config) => {
      // 从localStorage获取token（PC端）
      const token = typeof window !== 'undefined'
        ? localStorage.getItem('access_token')
        : null;

      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  client.interceptors.response.use(
    (response: AxiosResponse<ApiResponse<any>>) => {
      const { data } = response;

      // 处理业务错误码
      if (data.code !== 'SUCCESS' && data.code !== '200') {
        const error = new Error(data.message || '请求失败');
        (error as any).code = data.code;
        (error as any).response = response;
        return Promise.reject(error);
      }

      // 返回实际数据
      return data.data;
    },
    (error: AxiosError<ApiResponse<any>>) => {
      if (error.response) {
        const { status, data } = error.response;
        const customError = new Error(data?.message || error.message);
        (customError as any).status = status;
        (customError as any).code = data?.code;
        return Promise.reject(customError);
      }
      return Promise.reject(error);
    }
  );

  return client;
}

// 默认API客户端实例
export const apiClient = createApiClient({
  baseURL: typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL
    ? import.meta.env.VITE_API_BASE_URL
    : '/api',
});

// 请求工具函数
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return apiClient.get(url, config);
}

export async function post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return apiClient.post(url, data, config);
}

export async function put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return apiClient.put(url, data, config);
}

export async function patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return apiClient.patch(url, data, config);
}

export async function del<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return apiClient.delete(url, config);
}

export default apiClient;
