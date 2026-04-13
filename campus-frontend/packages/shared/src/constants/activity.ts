/**
 * 活动相关常量
 */

import { ActivityStatus, ActivityType } from '../api/types';

/** 活动状态显示映射 */
export const ActivityStatusMap: Record<ActivityStatus, { label: string; color: string }> = {
  [ActivityStatus.PLANNING]: { label: '策划中', color: '#909399' },
  [ActivityStatus.PENDING_APPROVAL]: { label: '待审批', color: '#E6A23C' },
  [ActivityStatus.APPROVED]: { label: '已批准', color: '#409EFF' },
  [ActivityStatus.REGISTERING]: { label: '报名中', color: '#67C23A' },
  [ActivityStatus.ONGOING]: { label: '进行中', color: '#67C23A' },
  [ActivityStatus.COMPLETED]: { label: '已结束', color: '#909399' },
  [ActivityStatus.CANCELLED]: { label: '已取消', color: '#F56C6C' },
  [ActivityStatus.REJECTED]: { label: '已驳回', color: '#F56C6C' },
};

/** 活动类型显示映射 */
export const ActivityTypeMap: Record<ActivityType, string> = {
  [ActivityType.LECTURE]: '讲座',
  [ActivityType.WORKSHOP]: '工作坊',
  [ActivityType.COMPETITION]: '竞赛',
  [ActivityType.SOCIAL]: '社交活动',
  [ActivityType.VOLUNTEER]: '志愿活动',
  [ActivityType.SPORTS]: '体育活动',
  [ActivityType.ART]: '艺术活动',
  [ActivityType.OTHER]: '其他',
};

/** 活动类型图标映射（用于移动端） */
export const ActivityTypeIcon: Record<ActivityType, string> = {
  [ActivityType.LECTURE]: '📚',
  [ActivityType.WORKSHOP]: '🔧',
  [ActivityType.COMPETITION]: '🏆',
  [ActivityType.SOCIAL]: '🎉',
  [ActivityType.VOLUNTEER]: '💝',
  [ActivityType.SPORTS]: '⚽',
  [ActivityType.ART]: '🎨',
  [ActivityType.OTHER]: '📌',
};

/** 活动状态流转规则 */
export const ActivityStatusFlow: Record<ActivityStatus, ActivityStatus[]> = {
  [ActivityStatus.PLANNING]: [ActivityStatus.PENDING_APPROVAL, ActivityStatus.CANCELLED],
  [ActivityStatus.PENDING_APPROVAL]: [ActivityStatus.APPROVED, ActivityStatus.REJECTED],
  [ActivityStatus.APPROVED]: [ActivityStatus.REGISTERING, ActivityStatus.CANCELLED],
  [ActivityStatus.REGISTERING]: [ActivityStatus.ONGOING, ActivityStatus.CANCELLED],
  [ActivityStatus.ONGOING]: [ActivityStatus.COMPLETED, ActivityStatus.CANCELLED],
  [ActivityStatus.COMPLETED]: [],
  [ActivityStatus.CANCELLED]: [],
  [ActivityStatus.REJECTED]: [ActivityStatus.PLANNING],
};

/** 分页默认配置 */
export const DEFAULT_PAGINATION = {
  page: 1,
  size: 10,
  sizes: [10, 20, 50, 100],
};

/** 活动评价星级选项 */
export const RATING_OPTIONS = [1, 2, 3, 4, 5];

/** 活动评价维度 */
export const EVALUATION_DIMENSIONS = [
  { key: 'participation', label: '参与度', description: '活动参与人数与互动情况' },
  { key: 'educational', label: '教育性', description: '知识传播与学习效果' },
  { key: 'innovation', label: '创新性', description: '活动形式与内容创新程度' },
  { key: 'influence', label: '影响力', description: '活动传播范围与社会影响' },
  { key: 'sustainability', label: '可持续性', description: '活动长期发展潜力' },
];
