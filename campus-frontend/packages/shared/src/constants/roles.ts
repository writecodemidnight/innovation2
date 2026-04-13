/**
 * 角色与权限相关常量
 */

import { UserRole } from '../api/types';

/** 角色显示映射 */
export const UserRoleMap: Record<UserRole, { label: string; color: string; description: string }> = {
  [UserRole.STUDENT]: {
    label: '学生',
    color: '#409EFF',
    description: '普通学生用户，可浏览和报名活动',
  },
  [UserRole.CLUB_MEMBER]: {
    label: '社团成员',
    color: '#67C23A',
    description: '社团普通成员，可参与社团活动管理',
  },
  [UserRole.CLUB_PRESIDENT]: {
    label: '社长',
    color: '#E6A23C',
    description: '社团负责人，可申报活动和预约资源',
  },
  [UserRole.ADMIN]: {
    label: '管理员',
    color: '#F56C6C',
    description: '系统管理员，可审批活动和分配资源',
  },
  [UserRole.SUPER_ADMIN]: {
    label: '超级管理员',
    color: '#8E44AD',
    description: '系统超级管理员，拥有所有权限',
  },
};

/** 角色权限集合 */
export const RolePermissions: Record<UserRole, string[]> = {
  [UserRole.STUDENT]: [
    'activity:view',
    'activity:join',
    'activity:evaluate',
    'profile:view',
    'profile:edit',
  ],
  [UserRole.CLUB_MEMBER]: [
    'activity:view',
    'activity:join',
    'activity:evaluate',
    'club:view',
    'profile:view',
    'profile:edit',
  ],
  [UserRole.CLUB_PRESIDENT]: [
    'activity:view',
    'activity:create',
    'activity:edit',
    'activity:delete',
    'activity:manage',
    'resource:view',
    'resource:reserve',
    'club:view',
    'club:manage',
    'club:members',
    'report:view',
    'profile:view',
    'profile:edit',
  ],
  [UserRole.ADMIN]: [
    'activity:view',
    'activity:approve',
    'resource:view',
    'resource:manage',
    'resource:allocate',
    'club:view',
    'club:approve',
    'user:view',
    'user:manage',
    'dashboard:view',
    'report:view',
    'report:export',
    'system:config',
  ],
  [UserRole.SUPER_ADMIN]: [
    '*', // 所有权限
  ],
};

/** 检查角色是否有权限 */
export function hasPermission(role: UserRole, permission: string): boolean {
  const permissions = RolePermissions[role];
  if (permissions.includes('*')) return true;
  return permissions.includes(permission);
}

/** 检查角色是否有任意一个权限 */
export function hasAnyPermission(role: UserRole, permissions: string[]): boolean {
  return permissions.some(p => hasPermission(role, p));
}

/** 检查角色是否有所有权限 */
export function hasAllPermissions(role: UserRole, permissions: string[]): boolean {
  return permissions.every(p => hasPermission(role, p));
}
