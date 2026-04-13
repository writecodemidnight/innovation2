/**
 * 活动相关类型定义
 */

import type { ApiResponse, PaginationData, Timestamp } from './common.js';

/**
 * 活动状态枚举
 * 与数据库activities.status对应
 */
export enum ActivityStatus {
  PLANNING = 'PLANNING',       // 策划中
  REGISTERING = 'REGISTERING', // 报名中
  ONGOING = 'ONGOING',         // 进行中
  COMPLETED = 'COMPLETED',     // 已结束
  CANCELLED = 'CANCELLED',     // 已取消
}

/**
 * 活动类型枚举
 * 与数据库activities.activity_type对应
 */
export enum ActivityType {
  LECTURE = 'LECTURE',         // 讲座
  WORKSHOP = 'WORKSHOP',       // 工作坊
  COMPETITION = 'COMPETITION', // 竞赛
  SOCIAL = 'SOCIAL',           // 社交活动
  VOLUNTEER = 'VOLUNTEER',     // 志愿活动
  SPORTS = 'SPORTS',           // 体育活动
  ARTS = 'ARTS',               // 艺术活动
  ACADEMIC = 'ACADEMIC',       // 学术活动
}

/**
 * 参与状态枚举
 */
export enum ParticipationStatus {
  REGISTERED = 'REGISTERED',   // 已报名
  CHECKED_IN = 'CHECKED_IN',   // 已签到
  CHECKED_OUT = 'CHECKED_OUT', // 已签退
  ABSENT = 'ABSENT',           // 缺席
  CANCELLED = 'CANCELLED',     // 已取消
}

/**
 * 活动实体
 * 与数据库activities表对应
 */
export interface Activity {
  id: number;
  title: string;
  description?: string;
  clubId: number;
  clubName?: string;
  organizerId: number;
  organizerName?: string;
  activityType: ActivityType;
  startTime: Timestamp;
  endTime: Timestamp;
  location: string;
  maxParticipants: number;
  currentParticipants: number;
  status: ActivityStatus;
  coverImageUrl?: string;
  createdAt: Timestamp;
  updatedAt?: Timestamp;
}

/**
 * 创建活动请求
 */
export interface CreateActivityRequest {
  title: string;
  description?: string;
  clubId: number;
  activityType: ActivityType;
  startTime: Timestamp;
  endTime: Timestamp;
  location: string;
  maxParticipants: number;
  coverImageUrl?: string;
}

/**
 * 更新活动请求
 */
export interface UpdateActivityRequest {
  title?: string;
  description?: string;
  activityType?: ActivityType;
  startTime?: Timestamp;
  endTime?: Timestamp;
  location?: string;
  maxParticipants?: number;
  coverImageUrl?: string;
  status?: ActivityStatus;
}

/**
 * 活动参与者
 */
export interface ActivityParticipant {
  id: number;
  activityId: number;
  userId: number;
  userName?: string;
  userAvatar?: string;
  participationStatus: ParticipationStatus;
  checkInTime?: Timestamp;
  checkOutTime?: Timestamp;
  feedback?: string;
  rating?: number;
  createdAt: Timestamp;
}

/**
 * 活动评价请求
 */
export interface ActivityEvaluationRequest {
  activityId: number;
  participationScore: number;
  organizationScore: number;
  contentScore: number;
  innovationScore: number;
  impactScore: number;
  feedback?: string;
  photos?: string[];
}

/**
 * 活动筛选参数
 */
export interface ActivityFilterParams {
  keyword?: string;
  clubId?: number;
  activityType?: ActivityType;
  status?: ActivityStatus;
  startDate?: Timestamp;
  endDate?: Timestamp;
  page?: number;
  size?: number;
}

/**
 * 推荐活动参数
 */
export interface RecommendActivitiesParams {
  userId?: number;
  limit?: number;
}

// API响应类型别名
export type ActivityApiResponse = ApiResponse<Activity>;
export type ActivityListApiResponse = ApiResponse<PaginationData<Activity>>;
export type ActivityParticipantListApiResponse = ApiResponse<ActivityParticipant[]>;
export type JoinActivityApiResponse = ApiResponse<{ success: boolean; message: string }>;
