import { apiClient } from '@campus/shared';
import { Endpoints } from '@campus/shared';
import type {
  Activity,
  ActivityCreateRequest,
  ActivityListParams,
} from '@campus/shared';

export interface ActivityListResponse {
  content: Activity[];
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
}

export interface ActivityParticipantDto {
  id: number;
  userId: number;
  userName: string;
  avatarUrl?: string;
  status: 'REGISTERED' | 'CHECKED_IN' | 'CANCELLED';
  registeredAt: string;
  checkedInAt?: string;
}

export const activityApi = {
  // 获取活动列表（分页）
  getList: (params: ActivityListParams) =>
    apiClient.get<ActivityListResponse>(Endpoints.activities.list, { params }),

  // 获取活动详情
  getById: (id: number) =>
    apiClient.get<Activity>(Endpoints.activities.detail(id)),

  // 创建活动
  create: (data: ActivityCreateRequest) =>
    apiClient.post<Activity>(Endpoints.activities.create, data),

  // 更新活动
  update: (id: number, data: ActivityCreateRequest) =>
    apiClient.put<Activity>(Endpoints.activities.update(id), data),

  // 删除活动
  delete: (id: number) =>
    apiClient.delete<void>(Endpoints.activities.delete(id)),

  // 提交审批
  submitForApproval: (id: number) =>
    apiClient.post<void>(`${Endpoints.activities.detail(id)}/submit`, {}),

  // 获取参与者列表
  getParticipants: (id: number) =>
    apiClient.get<ActivityParticipantDto[]>(`${Endpoints.activities.list}/${id}/participants`),
};
