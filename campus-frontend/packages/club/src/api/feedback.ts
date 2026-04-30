import { apiClient } from '@campus/shared/api/client.axios';
import { Endpoints } from '@campus/shared';
import type {
  Feedback,
  FeedbackStats,
  CreateFeedbackRequest,
  FeedbackQueryParams,
  PageResponse,
} from '@campus/shared';

export const feedbackApi = {
  /** 获取反馈列表 */
  getList: (params?: FeedbackQueryParams) =>
    apiClient.get<PageResponse<Feedback>>(Endpoints.feedback.list, { params }),

  /** 获取活动反馈列表 */
  getByActivity: (activityId: number, params?: Omit<FeedbackQueryParams, 'activityId'>) =>
    apiClient.get<PageResponse<Feedback>>(Endpoints.feedback.byActivity(activityId), { params }),

  /** 获取反馈统计 */
  getStats: (activityId: number) =>
    apiClient.get<FeedbackStats>(Endpoints.feedback.stats(activityId)),

  /** 获取反馈详情 */
  getDetail: (id: number) =>
    apiClient.get<Feedback>(Endpoints.feedback.detail(id)),

  /** 创建反馈 */
  create: (data: CreateFeedbackRequest) =>
    apiClient.post<Feedback>(Endpoints.feedback.create, data),

  /** 更新反馈 */
  update: (id: number, data: Partial<CreateFeedbackRequest>) =>
    apiClient.put<Feedback>(Endpoints.feedback.update(id), data),

  /** 删除反馈 */
  delete: (id: number) =>
    apiClient.delete<void>(Endpoints.feedback.delete(id)),
};
