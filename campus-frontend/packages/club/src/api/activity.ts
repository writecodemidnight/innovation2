import { apiClient } from '@campus/shared/api/client.axios';
import { Endpoints } from '@campus/shared';
import type {
  Activity,
  ActivityListParams,
  ActivityCreateRequest,
  ActivityEvaluationReport,
  PageResponse,
} from '@campus/shared';

export const activityApi = {
  /** 获取活动列表 */
  getList: (params?: ActivityListParams) =>
    apiClient.get<PageResponse<Activity>>(Endpoints.activities.list, { params }),

  /** 获取活动详情 */
  getDetail: (id: number) => apiClient.get<Activity>(Endpoints.activities.detail(id)),

  /** 获取活动详情 (别名) */
  getById: (id: number) => apiClient.get<Activity>(Endpoints.activities.detail(id)),

  /** 创建活动 */
  create: (data: ActivityCreateRequest) =>
    apiClient.post<Activity>(Endpoints.activities.create, data),

  /** 更新活动 */
  update: (id: number, data: Partial<ActivityCreateRequest>) =>
    apiClient.put<Activity>(Endpoints.activities.update(id), data),

  /** 删除活动 */
  delete: (id: number) => apiClient.delete<void>(Endpoints.activities.delete(id)),

  /** 获取活动评估报告 */
  getEvaluationReport: (id: number) =>
    apiClient.get<ActivityEvaluationReport>(Endpoints.evaluation.report(id)),

  /** 提交活动审批 */
  submitForApproval: (id: number) =>
    apiClient.post<void>(`${Endpoints.activities.list}/${id}/submit`),

  /** 获取活动参与者 */
  getParticipants: (id: number) =>
    apiClient.get<any[]>(`${Endpoints.activities.list}/${id}/participants`),
};
