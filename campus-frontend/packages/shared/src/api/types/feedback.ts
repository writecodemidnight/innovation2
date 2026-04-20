/**
 * 反馈评价类型定义
 */

/** 反馈评价 */
export interface Feedback {
  id: number;
  activityId: number;
  activityTitle?: string;
  userId: number;
  username?: string;
  avatar?: string;
  rating: number;
  content: string;
  images?: string[];
  createdAt: string;
  updatedAt?: string;
}

/** 创建反馈请求 */
export interface CreateFeedbackRequest {
  activityId: number;
  rating: number;
  content: string;
  images?: string[];
}

/** 反馈统计 */
export interface FeedbackStats {
  activityId: number;
  activityTitle?: string;
  averageRating: number;
  totalCount: number;
  ratingDistribution: RatingDistributionItem[];
}

/** 评分分布项 */
export interface RatingDistributionItem {
  stars: number;
  count: number;
  percentage: number;
}

/** 反馈查询参数 */
export interface FeedbackQueryParams {
  activityId?: number;
  userId?: number;
  rating?: number;
  page?: number;
  size?: number;
  sort?: string;
}

/** 反馈类型筛选 */
export enum FeedbackFilterType {
  ALL = 'all',
  POSITIVE = 'positive',
  NEGATIVE = 'negative',
}
