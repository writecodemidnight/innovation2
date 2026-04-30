/**
 * 学生活动相关 API
 */

import { apiClient, Endpoints } from '@campus/shared';
import type {
  Activity,
  ActivityDetail,
  PageResponse
} from '@campus/shared';

export const activityApi = {
  /**
   * 获取个性化推荐活动（基于K-Means聚类）
   */
  getRecommended(): Promise<Activity[]> {
    return apiClient.get(Endpoints.activities.recommend);
  },

  /**
   * 获取热门推荐活动
   */
  getHot(): Promise<Activity[]> {
    return apiClient.get(Endpoints.activities.hot);
  },

  /**
   * 获取即将开始的活动
   */
  getUpcoming(): Promise<Activity[]> {
    return apiClient.get(Endpoints.activities.upcoming);
  },

  /**
   * 获取活动列表
   */
  getList(params?: {
    page?: number;
    size?: number;
    type?: string;
    status?: string;
    keyword?: string;
  }): Promise<PageResponse<Activity>> {
    return apiClient.get(Endpoints.activities.list, { params });
  },

  /**
   * 获取活动详情
   */
  getDetail(id: number): Promise<ActivityDetail> {
    return apiClient.get(Endpoints.activities.detail(id));
  },

  /**
   * 报名活动
   */
  join(id: number): Promise<void> {
    return apiClient.post(Endpoints.activities.join(id));
  },

  /**
   * 取消报名
   */
  leave(id: number): Promise<void> {
    return apiClient.post(Endpoints.activities.leave(id));
  },

  /**
   * 提交活动评价
   */
  submitEvaluation(id: number, data: {
    rating: number;
    content: string;
    photos?: string[];
  }): Promise<void> {
    return apiClient.post(Endpoints.activities.evaluate(id), data);
  },

  /**
   * 获取活动评价列表
   */
  getEvaluations(id: number): Promise<any[]> {
    return apiClient.get(Endpoints.activities.evaluations(id));
  },

  /**
   * 获取我的活动列表
   */
  getMyActivities(): Promise<Activity[]> {
    return apiClient.get(`${Endpoints.activities.list}/my`);
  },

  /**
   * 签到活动
   */
  checkIn(id: number): Promise<void> {
    return apiClient.post(`${Endpoints.activities.detail(id)}/check-in`);
  },
};
