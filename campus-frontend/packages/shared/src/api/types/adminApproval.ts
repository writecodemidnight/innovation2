/**
 * 管理端审批类型定义
 */

/** 审批状态 */
export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED';

/** 审批类型 */
export type ApprovalType = 'ACTIVITY' | 'FUND' | 'RESOURCE';

/** 审批请求 */
export interface ApprovalRequest {
  comment?: string;
}

/** 审批统计 */
export interface ApprovalCounts {
  activities: number;
  resourceBookings: number;
  fundApplications?: number;
}

/** 审批历史统计 */
export interface HistoryCounts {
  activities: {
    approved: number;
    completed: number;
  };
  resourceBookings: {
    approved: number;
  };
  fundApplications: {
    approved: number;
    rejected: number;
  };
}

/** 资源预约 */
export interface ResourceBooking {
  id: number;
  resourceId: number;
  resourceName?: string;
  resourceType?: string;
  activityId?: number;
  activityTitle?: string;
  clubId?: number;
  applicantId?: number;
  applicantName?: string;
  startTime: string;
  endTime: string;
  attendees?: number;
  status: string;
  statusLabel?: string;
  remark?: string;
  approvedAt?: string;
  approvalRemark?: string;
  createdAt: string;
  updatedAt?: string;
}

// PageResponse is already exported from './fund'

export interface AdminApproval {
  id: number;
  type: ApprovalType;
  title: string;
  applicantName: string;
  clubName?: string;
  submitTime: string;
  status: ApprovalStatus;
}
