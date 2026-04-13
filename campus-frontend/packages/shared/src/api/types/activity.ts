/**
 * 活动相关类型定义
 * 与后端API和数据库表结构对应
 */

/** API统一响应格式 */
export interface ApiResponse<T> {
  code: string;
  message: string;
  data: T;
}

/** 活动状态枚举 */
export enum ActivityStatus {
  PLANNING = 'PLANNING',
  PENDING_APPROVAL = 'PENDING_APPROVAL',
  APPROVED = 'APPROVED',
  REGISTERING = 'REGISTERING',
  ONGOING = 'ONGOING',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
  REJECTED = 'REJECTED'
}

/** 活动类型枚举 */
export enum ActivityType {
  LECTURE = 'LECTURE',
  WORKSHOP = 'WORKSHOP',
  COMPETITION = 'COMPETITION',
  SOCIAL = 'SOCIAL',
  VOLUNTEER = 'VOLUNTEER',
  SPORTS = 'SPORTS',
  ART = 'ART',
  OTHER = 'OTHER'
}

/** 活动实体 */
export interface Activity {
  id: number;
  title: string;
  description: string;
  clubId: number;
  clubName?: string;
  organizerId: number;
  organizerName?: string;
  activityType: ActivityType;
  startTime: string;
  endTime: string;
  location: string;
  maxParticipants: number;
  currentParticipants: number;
  status: ActivityStatus;
  coverImageUrl: string;
  budget?: number;
  requiresResources: boolean;
  createdAt: string;
  updatedAt: string;
}

/** 活动列表查询参数 */
export interface ActivityListParams {
  page?: number;
  size?: number;
  keyword?: string;
  activityType?: ActivityType;
  status?: ActivityStatus;
  clubId?: number;
  startDate?: string;
  endDate?: string;
}

/** 创建活动请求 */
export interface ActivityCreateRequest {
  title: string;
  description: string;
  clubId: number;
  activityType: ActivityType;
  startTime: string;
  endTime: string;
  location: string;
  maxParticipants: number;
  coverImageUrl?: string;
  budget?: number;
  requiredResourceIds?: number[];
}

/** 更新活动请求 */
export interface ActivityUpdateRequest extends Partial<ActivityCreateRequest> {
  id: number;
}

/** 活动报名请求 */
export interface ActivityJoinRequest {
  activityId: number;
  remark?: string;
}

/** 活动评价请求 */
export interface ActivityEvaluateRequest {
  activityId: number;
  overallRating: number;
  contentRating: number;
  organizationRating: number;
  satisfactionRating: number;
  comment?: string;
  photos?: string[];
}

/** 活动评价维度数据 */
export interface ActivityEvaluationDimensions {
  participation: number;
  educational: number;
  innovation: number;
  influence: number;
  sustainability: number;
}

/** 活动评估报告 */
export interface ActivityEvaluationReport {
  activityId: number;
  activityTitle: string;
  dimensions: ActivityEvaluationDimensions;
  totalScore: number;
  participantCount: number;
  evaluationCount: number;
  averageRating: number;
  aiInsights?: string;
  improvementSuggestions?: string[];
}

/** 活动推荐项 */
export interface ActivityRecommendation {
  activity: Activity;
  matchScore: number;
  reason: string;
}

/** 响应类型别名 */
export type ActivityCreateResponse = ApiResponse<Activity>;
export type ActivityListResponse = ApiResponse<{ items: Activity[]; total: number }>;
export type ActivityDetailResponse = ApiResponse<Activity>;
export type ActivityEvaluationResponse = ApiResponse<ActivityEvaluationReport>;
export type ActivityRecommendationResponse = ApiResponse<ActivityRecommendation[]>;
