/**
 * 社团相关类型定义
 */

import type { ApiResponse, PaginationData, Timestamp, ID } from './common.js';

/**
 * 社团状态枚举
 */
export enum ClubStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  SUSPENDED = 'SUSPENDED',
}

/**
 * 社团实体
 * 与数据库clubs表对应
 */
export interface Club {
  id: number;
  name: string;
  description?: string;
  logoUrl?: string;
  presidentId: number;
  advisorId?: number;
  status: ClubStatus;
  memberCount: number;
  createdAt: Timestamp;
  updatedAt?: Timestamp;
}

/**
 * 创建社团请求
 */
export interface CreateClubRequest {
  name: string;
  description?: string;
  logoUrl?: string;
  presidentId: number;
  advisorId?: number;
}

/**
 * 更新社团请求
 */
export interface UpdateClubRequest {
  name?: string;
  description?: string;
  logoUrl?: string;
  presidentId?: number;
  advisorId?: number;
  status?: ClubStatus;
}

/**
 * 社团成员
 */
export interface ClubMember {
  id: number;
  clubId: number;
  userId: number;
  role: 'PRESIDENT' | 'VICE_PRESIDENT' | 'MEMBER';
  joinedAt: Timestamp;
  user?: {
    id: number;
    username: string;
    realName: string;
    avatarUrl?: string;
  };
}

// API响应类型别名
export type ClubApiResponse = ApiResponse<Club>;
export type ClubListApiResponse = ApiResponse<PaginationData<Club>>;
export type ClubMemberListApiResponse = ApiResponse<ClubMember[]>;
