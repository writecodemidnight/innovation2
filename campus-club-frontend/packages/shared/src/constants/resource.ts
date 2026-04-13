/**
 * 资源相关常量
 */

import { ResourceType, ResourceStatus, ReservationStatus } from '../api/types/resource.js';

/**
 * 资源类型映射
 */
export const ResourceTypeMap: Record<ResourceType, string> = {
  [ResourceType.VENUE]: '场地',
  [ResourceType.EQUIPMENT]: '设备',
  [ResourceType.BUDGET]: '经费',
  [ResourceType.MATERIAL]: '物料',
};

/**
 * 资源状态映射
 */
export const ResourceStatusMap: Record<ResourceStatus, { label: string; color: string; tagType: 'success' | 'warning' | 'danger' | 'info' }> = {
  [ResourceStatus.AVAILABLE]: { label: '可用', color: '#67C23A', tagType: 'success' },
  [ResourceStatus.IN_USE]: { label: '使用中', color: '#409EFF', tagType: 'info' },
  [ResourceStatus.MAINTENANCE]: { label: '维护中', color: '#E6A23C', tagType: 'warning' },
  [ResourceStatus.RESERVED]: { label: '已预约', color: '#909399', tagType: 'info' },
};

/**
 * 预约状态映射
 */
export const ReservationStatusMap: Record<ReservationStatus, { label: string; color: string; tagType: 'success' | 'warning' | 'danger' | 'info' }> = {
  [ReservationStatus.PENDING]: { label: '待审批', color: '#E6A23C', tagType: 'warning' },
  [ReservationStatus.APPROVED]: { label: '已通过', color: '#67C23A', tagType: 'success' },
  [ReservationStatus.REJECTED]: { label: '已拒绝', color: '#F56C6C', tagType: 'danger' },
  [ReservationStatus.CANCELLED]: { label: '已取消', color: '#909399', tagType: 'info' },
  [ReservationStatus.EXPIRED]: { label: '已过期', color: '#909399', tagType: 'info' },
};

/**
 * 资源类型选项
 */
export const ResourceTypeOptions = Object.entries(ResourceTypeMap).map(([value, label]) => ({
  value: value as ResourceType,
  label,
}));

/**
 * 资源状态选项
 */
export const ResourceStatusOptions = Object.entries(ResourceStatusMap).map(([value, item]) => ({
  value: value as ResourceStatus,
  label: item.label,
}));

/**
 * 预约状态选项
 */
export const ReservationStatusOptions = Object.entries(ReservationStatusMap).map(([value, item]) => ({
  value: value as ReservationStatus,
  label: item.label,
}));

/**
 * 默认预约时长（分钟）
 */
export const DEFAULT_RESERVATION_DURATION = 120;

/**
 * 预约提前时间限制（小时）
 */
export const MIN_RESERVATION_ADVANCE_HOURS = 24;
