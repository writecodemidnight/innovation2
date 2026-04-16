import { axiosClient } from '@campus/shared/api';
import { Endpoints } from '@campus/shared';
import type {
  Activity,
  ActivityListParams,
  ActivityCreateRequest,
  ActivityUpdateRequest,
  ActivityEvaluationReport,
} from '@campus/shared';

export interface PageResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
}

export const activityApi = {
  /** 获取活动列表 */
  getList: (params: ActivityListParams) =>
    axiosClient.apiClient.get<PageResponse<Activity>>(Endpoints.activities.list, { params }),

  /** 获取活动详情 */
  getDetail: (id: number) => axiosClient.apiClient.get<Activity>(Endpoints.activities.detail(id)),

  /** 创建活动 */
  create: (data: ActivityCreateRequest) =>
    axiosClient.apiClient.post<Activity>(Endpoints.activities.create, data),

  /** 更新活动 */
  update: (id: number, data: ActivityUpdateRequest) =>
    axiosClient.apiClient.put<Activity>(Endpoints.activities.update(id), data),

  /** 删除活动 */
  delete: (id: number) => axiosClient.apiClient.delete<void>(Endpoints.activities.delete(id)),

  /** 获取活动评估报告 */
  getEvaluationReport: (id: number) =>
    axiosClient.apiClient.get<ActivityEvaluationReport>(Endpoints.evaluation.report(id)),
};
