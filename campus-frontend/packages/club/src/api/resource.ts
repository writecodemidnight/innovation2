import { apiClient } from '@campus/shared';
import { Endpoints } from '@campus/shared';
import type {
  Resource,
  ResourceReservation,
  ReservationRequest,
} from '@campus/shared';

export const resourceApi = {
  /** 获取资源列表 */
  getList: (type?: string) => {
    const url = type
      ? `${Endpoints.resources.list}/type/${type}`
      : Endpoints.resources.list;
    return apiClient.get<Resource[]>(url);
  },

  /** 获取资源详情 */
  getDetail: (id: number) => apiClient.get<Resource>(Endpoints.resources.detail(id)),

  /** 获取我的预约列表 */
  getMyReservations: () =>
    apiClient.get<ResourceReservation[]>(`${Endpoints.resources.list}/bookings/my`),

  /** 创建预约 */
  createReservation: (data: ReservationRequest) =>
    apiClient.post<ResourceReservation>(`${Endpoints.resources.list}/bookings`, data),

  /** 取消预约 */
  cancelReservation: (id: number) =>
    apiClient.post<void>(`${Endpoints.resources.list}/bookings/${id}/cancel`),
};
