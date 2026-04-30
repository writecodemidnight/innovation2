/**
 * 社团相关类型定义
 */

/** 社团状态 */
export enum ClubStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  PENDING_APPROVAL = 'PENDING_APPROVAL',
  SUSPENDED = 'SUSPENDED'
}

/** 社团类型 */
export enum ClubCategory {
  ACADEMIC = 'ACADEMIC',
  ARTS = 'ARTS',
  SPORTS = 'SPORTS',
  VOLUNTEER = 'VOLUNTEER',
  TECHNOLOGY = 'TECHNOLOGY',
  CULTURE = 'CULTURE',
  OTHER = 'OTHER'
}

/** 社团类型标签映射 */
export const ClubCategoryMap: Record<ClubCategory, { label: string; color: string }> = {
  [ClubCategory.ACADEMIC]: { label: '学术科技', color: '#409EFF' },
  [ClubCategory.ARTS]: { label: '文化艺术', color: '#E6A23C' },
  [ClubCategory.SPORTS]: { label: '体育运动', color: '#67C23A' },
  [ClubCategory.VOLUNTEER]: { label: '公益志愿', color: '#F56C6C' },
  [ClubCategory.TECHNOLOGY]: { label: '科技创新', color: '#909399' },
  [ClubCategory.CULTURE]: { label: '传统文化', color: '#8B4513' },
  [ClubCategory.OTHER]: { label: '其他', color: '#606266' },
};

/** 社团实体 */
export interface Club {
  id: number;
  name: string;
  description: string;
  category: ClubCategory;
  status: ClubStatus;
  logoUrl?: string;
  foundedDate: string;
  memberCount: number;
  presidentId: number;
  presidentName?: string;
  advisorName?: string;
  contactEmail?: string;
  contactPhone?: string;
  createdAt: string;
  updatedAt: string;
}

/** 社团成员 */
export interface ClubMember {
  id: number;
  clubId: number;
  userId: number;
  userName?: string;
  realName?: string;
  avatarUrl?: string;
  role: 'PRESIDENT' | 'VICE_PRESIDENT' | 'MEMBER';
  joinDate: string;
  status: 'ACTIVE' | 'INACTIVE';
}

/** 社团统计数据 */
export interface ClubStatistics {
  clubId: number;
  clubName: string;
  totalActivities: number;
  totalParticipants: number;
  avgEvaluationScore: number;
  resourceUtilizationRate: number;
  monthlyActivityTrend: { month: string; count: number }[];
  topActivities: { id: number; title: string; participants: number }[];
}
