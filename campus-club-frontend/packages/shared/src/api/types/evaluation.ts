/**
 * 评估相关类型定义
 */

import type { ApiResponse, Timestamp } from './common.js';

/**
 * 评估指标类型枚举
 */
export enum MetricType {
  PARTICIPATION = 'PARTICIPATION',   // 参与度
  ORGANIZATION = 'ORGANIZATION',     // 组织质量
  CONTENT = 'CONTENT',               // 内容质量
  INNOVATION = 'INNOVATION',         // 创新性
  IMPACT = 'IMPACT',                 // 影响力
}

/**
 * 评估指标实体
 */
export interface EvaluationMetric {
  id: number;
  name: string;
  description?: string;
  metricType: MetricType;
  weight: number;
  maxScore: number;
  minScore: number;
  activityType?: string;
}

/**
 * 活动评估结果（五维模型）
 */
export interface ActivityEvaluation {
  activityId: number;
  participationScore: number;   // 参与度得分
  organizationScore: number;    // 组织质量得分
  contentScore: number;         // 内容质量得分
  innovationScore: number;      // 创新性得分
  impactScore: number;          // 影响力得分
  overallScore: number;         // 综合得分（AHP计算）
  generatedAt: Timestamp;
}

/**
 * 雷达图数据
 */
export interface RadarChartData {
  indicators: Array<{
    name: string;
    max: number;
  }>;
  series: Array<{
    name: string;
    value: number[];
  }>;
}

/**
 * 活动评估报告
 */
export interface ActivityEvaluationReport {
  activityId: number;
  activityTitle: string;
  evaluation: ActivityEvaluation;
  radarData: RadarChartData;
  participantCount: number;
  evaluationCount: number;
  avgRating: number;
  feedbackSummary?: string;
  recommendations?: string[];
}

/**
 * 反馈情感分析结果
 */
export interface SentimentAnalysisResult {
  positive: number;
  neutral: number;
  negative: number;
  keywords: string[];
}

/**
 * 评价反馈项
 */
export interface EvaluationFeedback {
  id: number;
  activityId: number;
  userId: number;
  userName?: string;
  rating: number;
  content?: string;
  photos?: string[];
  sentiment?: 'positive' | 'neutral' | 'negative';
  createdAt: Timestamp;
}

/**
 * 提交评估请求
 */
export interface SubmitEvaluationRequest {
  activityId: number;
  participationScore: number;
  organizationScore: number;
  contentScore: number;
  innovationScore: number;
  impactScore: number;
  feedback?: string;
  photos?: string[];
}

// API响应类型别名
export type EvaluationReportApiResponse = ApiResponse<ActivityEvaluationReport>;
export type RadarDataApiResponse = ApiResponse<RadarChartData>;
export type FeedbackListApiResponse = ApiResponse<EvaluationFeedback[]>;
export type SentimentAnalysisApiResponse = ApiResponse<SentimentAnalysisResult>;
