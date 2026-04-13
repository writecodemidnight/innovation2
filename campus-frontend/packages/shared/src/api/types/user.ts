/**
 * 用户相关类型定义
 */

/** 用户角色枚举 */
export enum UserRole {
  STUDENT = 'STUDENT',
  CLUB_MEMBER = 'CLUB_MEMBER',
  CLUB_PRESIDENT = 'CLUB_PRESIDENT',
  ADMIN = 'ADMIN',
  SUPER_ADMIN = 'SUPER_ADMIN'
}

/** 用户状态 */
export enum UserStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  SUSPENDED = 'SUSPENDED'
}

/** 用户实体 */
export interface User {
  id: number;
  username: string;
  email?: string;
  phone?: string;
  realName: string;
  studentId?: string;
  avatarUrl?: string;
  role: UserRole;
  status: UserStatus;
  clubId?: number;
  clubName?: string;
  department?: string;
  major?: string;
  grade?: string;
  createdAt: string;
  updatedAt: string;
}

/** 登录请求 */
export interface LoginRequest {
  username: string;
  password: string;
}

/** 微信登录请求 */
export interface WechatLoginRequest {
  code: string;
  encryptedData?: string;
  iv?: string;
}

/** 登录响应 */
export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  user: User;
}

/** 注册请求 */
export interface RegisterRequest {
  username: string;
  password: string;
  realName: string;
  studentId: string;
  email?: string;
  phone?: string;
}

/** 更新用户资料请求 */
export interface UpdateProfileRequest {
  realName?: string;
  email?: string;
  phone?: string;
  avatarUrl?: string;
  department?: string;
  major?: string;
}

/** 修改密码请求 */
export interface ChangePasswordRequest {
  oldPassword: string;
  newPassword: string;
}

/** 用户活动参与统计 */
export interface UserParticipationStats {
  totalActivities: number;
  totalHours: number;
  byType: Record<string, number>;
  monthlyTrend: { month: string; count: number }[];
}
