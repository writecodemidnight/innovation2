/**
 * 反馈评价相关 API
 */

import { apiClient, Endpoints } from '@campus/shared';

export interface FeedbackRequest {
  activityId: number;
  rating: number;
  organizationRating?: number;
  contentRating?: number;
  content: string;
  images?: string[];
}

export interface Feedback {
  id: number;
  activityId: number;
  userId: number;
  rating: number;
  organizationRating?: number;
  contentRating?: number;
  content: string;
  images?: string[];
  sentimentScore?: number;
  sentimentLevel?: string;
  keywords?: string[];
  createdAt: string;
}

export const feedbackApi = {
  /**
   * 提交活动评价
   */
  submit(data: FeedbackRequest): Promise<Feedback> {
    return apiClient.post(Endpoints.feedback.create, data);
  },

  /**
   * 获取活动的评价列表
   */
  getByActivity(activityId: number): Promise<Feedback[]> {
    return apiClient.get(Endpoints.feedback.byActivity(activityId));
  },

  /**
   * 检查用户是否已评价
   */
  async hasFeedback(activityId: number): Promise<boolean> {
    if (!activityId || isNaN(activityId)) {
      console.warn('hasFeedback: invalid activityId', activityId);
      return false;
    }
    try {
      const result = await apiClient.get<boolean>(
        `${Endpoints.feedback.byActivity(activityId)}/has-feedback`
      );
      return result || false;
    } catch {
      return false;
    }
  },

  /**
   * 获取我的评价列表
   */
  async getMyList(params?: { page?: number; size?: number }): Promise<{
    content: any[];
    totalElements: number;
  }> {
    const response = await apiClient.get<any>(Endpoints.feedback.my, { params });
    // 假设后端返回的是分页数据
    return {
      content: response.content || [],
      totalElements: response.totalElements || 0,
    };
  },
};
