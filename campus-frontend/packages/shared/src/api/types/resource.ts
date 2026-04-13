/**
 * 资源相关类型定义
 */

/** 资源类型 */
export enum ResourceType {
  CLASSROOM = 'CLASSROOM',
  AUDITORIUM = 'AUDITORIUM',
  SPORTS_FIELD = 'SPORTS_FIELD',
  MEETING_ROOM = 'MEETING_ROOM',
  EQUIPMENT = 'EQUIPMENT',
  AUDIO_VISUAL = 'AUDIO_VISUAL',
  OTHER = 'OTHER'
}

/** 资源状态 */
export enum ResourceStatus {
  AVAILABLE = 'AVAILABLE',
  IN_USE = 'IN_USE',
  MAINTENANCE = 'MAINTENANCE',
  RESERVED = 'RESERVED'
}

/** 预约状态 */
export enum ReservationStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  CANCELLED = 'CANCELLED',
  COMPLETED = 'COMPLETED'
}

/** 资源实体 */
export interface Resource {
  id: number;
  name: string;
  type: ResourceType;
  location: string;
  capacity?: number;
  description?: string;
  status: ResourceStatus;
  images?: string[];
  amenities?: string[];
  hourlyRate?: number;
  managedBy?: number;
  createdAt: string;
  updatedAt: string;
}

/** 资源预约 */
export interface ResourceReservation {
  id: number;
  resourceId: number;
  resourceName?: string;
  activityId: number;
  activityTitle?: string;
  clubId: number;
  clubName?: string;
  applicantId: number;
  applicantName?: string;
  startTime: string;
  endTime: string;
  purpose: string;
  attendeesCount?: number;
  status: ReservationStatus;
  adminComment?: string;
  createdAt: string;
  updatedAt: string;
}

/** 预约请求 */
export interface ReservationRequest {
  resourceId: number;
  activityId: number;
  startTime: string;
  endTime: string;
  purpose: string;
  attendeesCount?: number;
}

/** 资源池统计 */
export interface ResourcePoolStats {
  totalResources: number;
  byType: Record<ResourceType, number>;
  utilizationRate: number;
  pendingReservations: number;
  todayReservations: number;
}

/** 资源使用热力图数据 */
export interface ResourceHeatmapData {
  resourceId: number;
  resourceName: string;
  hourlyUsage: boolean[];
}
