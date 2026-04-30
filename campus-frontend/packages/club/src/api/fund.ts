import { apiClient } from '@campus/shared/api/client.axios';
import { Endpoints } from '@campus/shared';
import type { FundApplication, FundApplyRequest, PageResponse } from '@campus/shared';

export const fundApi = {
  /** 提交资金申请 */
  apply: (data: FundApplyRequest) =>
    apiClient.post<FundApplication>(Endpoints.funds.applications, data),

  /** 获取我的资金申请列表 */
  getMyApplications: (page = 0, size = 10) =>
    apiClient.get<PageResponse<FundApplication>>(Endpoints.funds.myApplications, {
      params: { page, size }
    }),

  /** 获取社团资金申请列表 */
  getClubApplications: (page = 0, size = 10) =>
    apiClient.get<PageResponse<FundApplication>>(Endpoints.funds.clubApplications, {
      params: { page, size }
    }),

  /** 获取资金申请详情 */
  getApplication: (id: number) =>
    apiClient.get<FundApplication>(Endpoints.funds.applicationDetail(id)),

  /** 取消资金申请 */
  cancel: (id: number, reason?: string) =>
    apiClient.post<void>(Endpoints.funds.cancel(id), null, {
      params: { reason }
    }),
};
