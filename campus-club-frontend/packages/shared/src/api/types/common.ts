/**
 * 通用API类型定义
 */

/**
 * 统一API响应格式
 * 与后端ApiResponse<T>对应
 */
export interface ApiResponse<T> {
  code: string;
  message: string;
  data: T;
}

/**
 * 分页请求参数
 */
export interface PaginationParams {
  page?: number;
  size?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

/**
 * 分页响应数据
 */
export interface PaginationData<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
  first: boolean;
  last: boolean;
}

/**
 * API错误
 */
export interface ApiError {
  code: string;
  message: string;
  details?: string;
}

/**
 * 通用ID类型
 */
export type ID = number | string;

/**
 * 时间戳类型（ISO 8601格式字符串）
 */
export type Timestamp = string;

/**
 * 操作结果
 */
export interface OperationResult {
  success: boolean;
  message: string;
}
