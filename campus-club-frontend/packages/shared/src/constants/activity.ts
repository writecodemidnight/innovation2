/**
 * 活动相关常量
 */

import { ActivityStatus, ActivityType, ParticipationStatus } from '../api/types/activity.js';

/**
 * 活动状态映射（用于UI展示）
 */
export const ActivityStatusMap: Record<ActivityStatus, { label: string; color: string }> = {
  [ActivityStatus.PLANNING]: { label: '策划中', color: '#909399' },
  [ActivityStatus.REGISTERING]: { label: '报名中', color: '#67C23A' },
  [ActivityStatus.ONGOING]: { label: '进行中', color: '#409EFF' },
  [ActivityStatus.COMPLETED]: { label: '已结束', color: '#E6A23C' },
  [ActivityStatus.CANCELLED]: { label: '已取消', color: '#F56C6C' },
};

/**
 * 活动类型映射
 */
export const ActivityTypeMap: Record<ActivityType, string> = {
  [ActivityType.LECTURE]: '讲座',
  [ActivityType.WORKSHOP]: '工作坊',
  [ActivityType.COMPETITION]: '竞赛',
  [ActivityType.SOCIAL]: '社交活动',
  [ActivityType.VOLUNTEER]: '志愿活动',
  [ActivityType.SPORTS]: '体育活动',
  [ActivityType.ARTS]: '艺术活动',
  [ActivityType.ACADEMIC]: '学术活动',
};

/**
 * 参与状态映射
 */
export const ParticipationStatusMap: Record<ParticipationStatus, string> = {
  [ParticipationStatus.REGISTERED]: '已报名',
  [ParticipationStatus.CHECKED_IN]: '已签到',
  [ParticipationStatus.CHECKED_OUT]: '已签退',
  [ParticipationStatus.ABSENT]: '缺席',
  [ParticipationStatus.CANCELLED]: '已取消',
};

/**
 * 活动类型选项（用于表单选择）
 */
export const ActivityTypeOptions = Object.entries(ActivityTypeMap).map(([value, label]) => ({
  value: value as ActivityType,
  label,
}));

/**
 * 活动状态选项
 */
export const ActivityStatusOptions = Object.entries(ActivityStatusMap).map(([value, item]) => ({
  value: value as ActivityStatus,
  label: item.label,
}));

/**
 * 默认分页配置
 */
export const DEFAULT_PAGE_SIZE = 10;
export const MAX_PAGE_SIZE = 100;
