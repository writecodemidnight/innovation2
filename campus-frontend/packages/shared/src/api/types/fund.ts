/**
 * 资金管理类型定义
 */

/** 资金申请状态 */
export enum FundStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  CANCELLED = 'CANCELLED',
}

/** 资金申请 */
export interface FundApplication {
  id: number;
  clubId: number;
  clubName?: string;
  activityId?: number;
  activityTitle?: string;
  applicantId: number;
  applicantName?: string;
  amount: number;
  purpose: string;
  budgetBreakdown?: string;
  status: FundStatus;
  reviewerId?: number;
  reviewerName?: string;
  reviewerComment?: string;
  createdAt: string;
  reviewedAt?: string;
  cancelledAt?: string;
  cancelReason?: string;
}

/** 资金申请请求 */
export interface FundApplyRequest {
  activityId?: number;
  amount: number;
  purpose: string;
  budgetBreakdown?: string;
}

/** 资金审批请求 */
export interface FundReviewRequest {
  comment?: string;
}

/** 分页响应 */
export interface PageResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
}
