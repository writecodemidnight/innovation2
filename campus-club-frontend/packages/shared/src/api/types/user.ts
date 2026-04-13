/**
 * 用户相关类型定义
 */

import type { ApiResponse, PaginationData, Timestamp } from './common.js';

/**
 * 用户角色枚举
 * 与数据库roles表对应
 */
export enum UserRole {
  ADMIN = 'ADMIN',
  TEACHER = 'TEACHER',
  CLUB_PRESIDENT = 'CLUB_PRESIDENT',
  CLUB_MEMBER = 'CLUB_MEMBER',
  STUDENT = 'STUDENT',
}

/**
 * 用户实体
 * 与数据库users表对应
 */
export interface User {
  id: number;
  username: string;
  email: string;
  realName: string;
  studentId?: string;
  phone?: string;
  avatarUrl?: string;
  roleId: number;
  role?: UserRole;
  createdAt: Timestamp;
  updatedAt?: Timestamp;
}

/**
 * 登录请求
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * 登录响应
 */
export interface LoginResponse {
  token: string;
  refreshToken: string;
  expiresIn: number;
  user: User;
}

/**
 * 微信登录请求
 */
export interface WxLoginRequest {
  code: string;
}

/**
 * 更新用户信息请求
 */
export interface UpdateUserRequest {
  realName?: string;
  phone?: string;
  email?: string;
  avatarUrl?: string;
}

/**
 * 修改密码请求
 */
export interface ChangePasswordRequest {
  oldPassword: string;
  newPassword: string;
}

// API响应类型别名
export type LoginApiResponse = ApiResponse<LoginResponse>;
export type UserApiResponse = ApiResponse<User>;
export type UserListApiResponse = ApiResponse<PaginationData<User>>;
