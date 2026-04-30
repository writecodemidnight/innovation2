import { apiClient } from '@campus/shared';

/**
 * 预测活动参与度
 */
export const predictParticipation = async (data: {
  activityType: string;
  venueType: string;
  plannedDate: string;
  historicalData?: Array<{ date: string; value: number }>;
}) => {
  return apiClient.post('/api/v1/club/algorithm/predict-participation', data);
};

/**
 * 分析活动反馈情感
 */
export const analyzeFeedback = async (data: {
  activityId: string;
  feedbacks: Array<{ studentId: string; text: string }>;
}) => {
  return apiClient.post('/api/v1/club/algorithm/analyze-feedback', data);
};

/**
 * 单条文本情感分析
 */
export const analyzeSentiment = async (text: string) => {
  return apiClient.post('/api/v1/club/algorithm/sentiment', { text });
};

/**
 * 算法API统一导出
 */
export const algorithmApi = {
  predictParticipation,
  analyzeFeedback,
  analyzeSentiment,
};
