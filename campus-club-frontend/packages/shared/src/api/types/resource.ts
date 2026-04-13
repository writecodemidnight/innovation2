/**
 * 资源相关类型定义
 */

import type { ApiResponse, PaginationData, Timestamp } from './common.js';

/**
 * 资源类型枚举
 */
export enum ResourceType {
  VENUE = 'VENUE',       // 场地
  EQUIPMENT = 'EQUIPMENT', // 设备
  BUDGET = 'BUDGET',     // 经费
  MATERIAL = 'MATERIAL', // 物料
}

/**
 * 资源状态枚举
 */
export enum ResourceStatus {
  AVAILABLE = 'AVAILABLE',     // 可用
  IN_USE = 'IN_USE',           // 使用中
  MAINTENANCE = 'MAINTENANCE', // 维护中
  RESERVED = 'RESERVED',       // 已预约
}

/**
 * 预约状态枚举
 */
export enum ReservationStatus {
  PENDING = 'PENDING',     // 待审批
  APPROVED = 'APPROVED',   // 已通过
  REJECTED = 'REJECTED',   // 已拒绝
  CANCELLED = 'CANCELLED', // 已取消
  EXPIRED = 'EXPIRED',     // 已过期
}

/**
 * 资源实体
 * 与数据库resources表对应
 */
export interface Resource {
  id: number;
  name: string;
  description?: string;
  resourceType: ResourceType;
  location?: string;
  capacity?: number;
  status: ResourceStatus;
  clubId?: number;
  clubName?: string;
  createdAt: Timestamp;
  updatedAt?: Timestamp;
}

/**
 * 资源预约
 * 与数据库resource_reservations表对应
 */
export interface ResourceReservation {
  id: number;
  resourceId: number;
  resourceName?: string;
  activityId?: number;
  activityTitle?: string;
  userId: number;
  userName?: string;
  startTime: Timestamp;
  endTime: Timestamp;
  status: ReservationStatus;
  purpose?: string;
  createdAt: Timestamp;
  updatedAt?: Timestamp;
}

/**
 * 创建资源请求
 */
export interface CreateResourceRequest {
  name: string;
  description?: string;
  resourceType: ResourceType;
  location?: string;
  capacity?: number;
  clubId?: number;
}

/**
 * 更新资源请求
 */
export interface UpdateResourceRequest {
  name?: string;
  description?: string;
  location?: string;
  capacity?: number;
  status?: ResourceStatus;
}

/**
 * 创建预约请求
 */
export interface CreateReservationRequest {
  resourceId: number;
  activityId?: number;
  startTime: Timestamp;
  endTime: Timestamp;
  purpose?: string;
}

/**
 * 资源日历项
 */
export interface ResourceCalendarItem {
  resourceId: number;
  resourceName: string;
  date: string;
  reservations: Array<{
    id: number;
    startTime: Timestamp;
    endTime: Timestamp;
    status: ReservationStatus;
    activityTitle?: string;
  }>;
}

/**
 * 资源筛选参数
 */
export interface ResourceFilterParams {
  keyword?: string;
  resourceType?: ResourceType;
  status?: ResourceStatus;
  clubId?: number;
  page?: number;
  size?: number;
}

// API响应类型别名
export type ResourceApiResponse = ApiResponse<Resource>;
export type ResourceListApiResponse = ApiResponse<PaginationData<Resource>>;
export type ReservationApiResponse = ApiResponse<ResourceReservation>;
export type ReservationListApiResponse = ApiResponse<ResourceReservation[]>;
export type ResourceCalendarApiResponse = ApiResponse<ResourceCalendarItem[]>;
