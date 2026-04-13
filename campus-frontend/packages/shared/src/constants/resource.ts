/**
 * 资源相关常量
 */

import { ResourceType, ResourceStatus, ReservationStatus } from '../api/types';

/** 资源类型显示映射 */
export const ResourceTypeMap: Record<ResourceType, string> = {
  [ResourceType.CLASSROOM]: '教室',
  [ResourceType.AUDITORIUM]: '礼堂',
  [ResourceType.SPORTS_FIELD]: '运动场地',
  [ResourceType.MEETING_ROOM]: '会议室',
  [ResourceType.EQUIPMENT]: '设备器材',
  [ResourceType.AUDIO_VISUAL]: '音视频设备',
  [ResourceType.OTHER]: '其他',
};

/** 资源类型图标 */
export const ResourceTypeIcon: Record<ResourceType, string> = {
  [ResourceType.CLASSROOM]: '🏫',
  [ResourceType.AUDITORIUM]: '🎭',
  [ResourceType.SPORTS_FIELD]: '⚽',
  [ResourceType.MEETING_ROOM]: '🤝',
  [ResourceType.EQUIPMENT]: '🔧',
  [ResourceType.AUDIO_VISUAL]: '📹',
  [ResourceType.OTHER]: '📦',
};

/** 资源状态显示映射 */
export const ResourceStatusMap: Record<ResourceStatus, { label: string; color: string; tag: string }> = {
  [ResourceStatus.AVAILABLE]: { label: '可用', color: '#67C23A', tag: 'success' },
  [ResourceStatus.IN_USE]: { label: '使用中', color: '#409EFF', tag: 'primary' },
  [ResourceStatus.MAINTENANCE]: { label: '维护中', color: '#E6A23C', tag: 'warning' },
  [ResourceStatus.RESERVED]: { label: '已预约', color: '#909399', tag: 'info' },
};

/** 预约状态显示映射 */
export const ReservationStatusMap: Record<ReservationStatus, { label: string; color: string; tag: string }> = {
  [ReservationStatus.PENDING]: { label: '待审批', color: '#E6A23C', tag: 'warning' },
  [ReservationStatus.APPROVED]: { label: '已通过', color: '#67C23A', tag: 'success' },
  [ReservationStatus.REJECTED]: { label: '已驳回', color: '#F56C6C', tag: 'danger' },
  [ReservationStatus.CANCELLED]: { label: '已取消', color: '#909399', tag: 'info' },
  [ReservationStatus.COMPLETED]: { label: '已完成', color: '#409EFF', tag: 'primary' },
};

/** 时间段配置（用于资源预约日历） */
export const TIME_SLOTS = [
  '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
  '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
  '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
  '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
  '20:00', '20:30', '21:00', '21:30', '22:00',
];

/** 星期显示 */
export const WEEK_DAYS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];

/** 资源预约提前天数限制 */
export const RESERVATION_ADVANCE_DAYS = {
  min: 1,  // 最少提前1天
  max: 30, // 最多提前30天
};

/** 单次预约最长时间（小时） */
export const MAX_RESERVATION_HOURS = 8;
