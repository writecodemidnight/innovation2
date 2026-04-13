/**
 * API客户端封装
 * 基于uni.request的统一请求处理，兼容uni-app所有平台
 */

import type { ApiResponse } from './types';

// API配置接口
export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  withCredentials?: boolean;
}

// 请求配置接口
export interface RequestConfig {
  params?: Record<string, any>;
  data?: any;
  headers?: Record<string, string>;
  timeout?: number;
}

// 统一错误类型
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// 构建完整URL
function buildURL(baseURL: string, url: string, params?: Record<string, any>): string {
  // 确保URL以/开头
  const fullPath = url.startsWith('/') ? url : `/${url}`;
  let fullURL = baseURL + fullPath;

  // 添加查询参数
  if (params && Object.keys(params).length > 0) {
    const queryString = Object.entries(params)
      .filter(([_, value]) => value !== undefined && value !== null)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
      .join('&');
    if (queryString) {
      fullURL += (fullURL.includes('?') ? '&' : '?') + queryString;
    }
  }

  return fullURL;
}

// 获取token
function getToken(): string | null {
  // 在uni-app环境中使用uni.getStorageSync
  if (typeof uni !== 'undefined') {
    return uni.getStorageSync('access_token') || null;
  }
  // 在浏览器环境中使用localStorage
  if (typeof window !== 'undefined' && window.localStorage) {
    return localStorage.getItem('access_token');
  }
  return null;
}

// 发送请求
function request<T>(
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
  url: string,
  config: RequestConfig = {},
  apiConfig: ApiClientConfig
): Promise<T> {
  return new Promise((resolve, reject) => {
    const fullURL = buildURL(apiConfig.baseURL, url, config.params);
    const token = getToken();

    const header: Record<string, string> = {
      'Content-Type': 'application/json',
      ...config.headers,
    };

    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    uni.request({
      url: fullURL,
      method,
      data: config.data,
      header,
      timeout: config.timeout || apiConfig.timeout || 30000,
      withCredentials: apiConfig.withCredentials ?? true,
      success: (res) => {
        const data = res.data as ApiResponse<T>;

        // 处理HTTP错误
        if (res.statusCode < 200 || res.statusCode >= 300) {
          reject(
            new ApiError(
              data?.message || `HTTP Error: ${res.statusCode}`,
              res.statusCode,
              data?.code,
              data
            )
          );
          return;
        }

        // 处理业务错误码
        if (data && data.code !== 'SUCCESS' && data.code !== '200') {
          reject(
            new ApiError(
              data.message || '请求失败',
              res.statusCode,
              data.code,
              data
            )
          );
          return;
        }

        // 返回实际数据
        resolve(data.data);
      },
      fail: (err) => {
        reject(new ApiError(err.errMsg || '网络请求失败'));
      },
    });
  });
}

// 创建API客户端
export function createApiClient(config: ApiClientConfig) {
  return {
    get: <T>(url: string, config_?: RequestConfig) =>
      request<T>('GET', url, config_, config),
    post: <T>(url: string, data?: any, config_?: RequestConfig) =>
      request<T>('POST', url, { ...config_, data }, config),
    put: <T>(url: string, data?: any, config_?: RequestConfig) =>
      request<T>('PUT', url, { ...config_, data }, config),
    patch: <T>(url: string, data?: any, config_?: RequestConfig) =>
      request<T>('PATCH', url, { ...config_, data }, config),
    delete: <T>(url: string, config_?: RequestConfig) =>
      request<T>('DELETE', url, config_, config),
  };
}

// API客户端类型
export type ApiClient = ReturnType<typeof createApiClient>;

// 默认API客户端实例
export const apiClient = createApiClient({
  baseURL:
    typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL
      ? import.meta.env.VITE_API_BASE_URL
      : '/api',
});

// 请求工具函数
export async function get<T>(url: string, config?: RequestConfig): Promise<T> {
  return apiClient.get<T>(url, config);
}

export async function post<T>(
  url: string,
  data?: any,
  config?: RequestConfig
): Promise<T> {
  return apiClient.post<T>(url, data, config);
}

export async function put<T>(
  url: string,
  data?: any,
  config?: RequestConfig
): Promise<T> {
  return apiClient.put<T>(url, data, config);
}

export async function patch<T>(
  url: string,
  data?: any,
  config?: RequestConfig
): Promise<T> {
  return apiClient.patch<T>(url, data, config);
}

export async function del<T>(url: string, config?: RequestConfig): Promise<T> {
  return apiClient.delete<T>(url, config);
}

export default apiClient;
